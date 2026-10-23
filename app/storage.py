from pathlib import Path
import hashlib
import os
import tempfile
import time

from python_multipart.exceptions import MultipartParseError
from python_multipart.multipart import MultipartParser, parse_options_header
from starlette.concurrency import run_in_threadpool

from .config import settings
from . import app_settings


def shard_dir(name: str) -> Path:
    shard = name[:2].lower()
    path = settings.data_dir / shard
    path.mkdir(parents=True, exist_ok=True)
    return path


class UploadTooLarge(ValueError):
    pass


class BadUpload(ValueError):
    pass


class DiskFull(OSError):
    pass


_FLUSH_BYTES = 1024 * 1024


def _decode_header(value: bytes) -> str:
    try:
        return value.decode("utf-8")
    except UnicodeDecodeError:
        return value.decode("latin-1")


def _write_chunk(out, sha, data: bytes):
    sha.update(data)
    out.write(data)


def _finish_file(out):
    out.flush()
    os.fsync(out.fileno())
    out.close()


async def save_upload_stream(request, stored_name: str, field_name: str = "file", on_disk_full=None):
    """直接解析 multipart 请求体, 把文件字段边收边写进 data 目录。

    不经过 Starlette 的 request.form(): 那条路会先把整个文件落到 /tmp
    (SpooledTemporaryFile), 再由我们复制一遍; 且客户端中途断开时
    (ClientDisconnect) 它不会关闭临时文件, /tmp 为 tmpfs 时这部分内存要等 GC 才释放。

    返回 (rel_path, size, sha256_hex, filename, content_type)。
    任何异常 (超限 / 格式错误 / 客户端断开 / 取消) 都会关闭并删除半成品临时文件。
    on_disk_full(need_bytes) -> bool: 写入途中磁盘不够时调用 (在线程池里), 返回 True 表示已腾出空间可继续。
    """
    _, params = parse_options_header(request.headers.get("content-type", ""))
    boundary = params.get(b"boundary")
    if not boundary:
        raise BadUpload("missing multipart boundary")

    target_dir = shard_dir(stored_name)
    temp_fd, temp_path = tempfile.mkstemp(prefix=".upload-", dir=target_dir)
    out = os.fdopen(temp_fd, "wb")
    sha = hashlib.sha256()
    total = 0
    pending: list[bytes] = []
    pending_len = 0
    # 非文件字段 (以及多余的文件) 只计数丢弃, 限制总请求体大小防滥用。
    received = 0
    limit = settings.max_upload_bytes  # None = 不限制
    try:
        expected = int(request.headers.get("content-length") or 0)
    except ValueError:
        expected = 0
    max_body = limit + 4 * 1024 * 1024 if limit is not None else None

    state = {"header_field": b"", "header_value": b"", "headers": {}, "in_target": False, "done": False,
             "filename": None, "content_type": None}

    def on_part_begin():
        state["headers"] = {}
        state["in_target"] = False

    def on_header_field(data, start, end):
        state["header_field"] += data[start:end]

    def on_header_value(data, start, end):
        state["header_value"] += data[start:end]

    def on_header_end():
        state["headers"][state["header_field"].lower()] = state["header_value"]
        state["header_field"] = b""
        state["header_value"] = b""

    def on_headers_finished():
        _, opts = parse_options_header(state["headers"].get(b"content-disposition", b""))
        if not state["done"] and opts.get(b"name") == field_name.encode() and b"filename" in opts:
            state["in_target"] = True
            state["filename"] = _decode_header(opts[b"filename"])
            ct = state["headers"].get(b"content-type")
            state["content_type"] = _decode_header(ct) if ct else None

    def on_part_data(data, start, end):
        nonlocal pending_len
        if state["in_target"]:
            pending.append(data[start:end])
            pending_len += end - start

    def on_part_end():
        if state["in_target"]:
            state["in_target"] = False
            state["done"] = True

    parser = MultipartParser(boundary, {
        "on_part_begin": on_part_begin,
        "on_part_data": on_part_data,
        "on_part_end": on_part_end,
        "on_header_field": on_header_field,
        "on_header_value": on_header_value,
        "on_header_end": on_header_end,
        "on_headers_finished": on_headers_finished,
    })

    async def flush():
        nonlocal total, pending_len
        data = b"".join(pending)
        pending.clear()
        pending_len = 0
        total += len(data)
        if limit is not None and total > limit:
            raise UploadTooLarge("file too large")
        # 不限大小时可能把磁盘写满: 剩余空间低于保留值就中止 (statvfs 很便宜, 每 MB 查一次无妨)
        if app_settings.upload_capacity_bytes() < len(data):
            # 还没收完的部分也要放得下 (按请求头里的总长度估算)
            need = max(len(data), expected - received + len(data))
            if not (on_disk_full and await run_in_threadpool(on_disk_full, need)):
                raise DiskFull("not enough disk space")
        # 写盘 / 算哈希放到线程池, 不阻塞事件循环。
        await run_in_threadpool(_write_chunk, out, sha, data)

    try:
        async for chunk in request.stream():
            received += len(chunk)
            if max_body is not None and received > max_body:
                raise UploadTooLarge("request body too large")
            try:
                parser.write(chunk)
            except MultipartParseError as exc:
                raise BadUpload(str(exc)) from exc
            if pending_len >= _FLUSH_BYTES:
                await flush()
        try:
            parser.finalize()
        except MultipartParseError as exc:
            raise BadUpload(str(exc)) from exc
        if pending:
            await flush()
        if not state["done"]:
            raise BadUpload(f"missing file field '{field_name}'")
        await run_in_threadpool(_finish_file, out)
        final = target_dir / stored_name
        os.replace(temp_path, final)
        return (str(final.relative_to(settings.data_dir)), total, sha.hexdigest(),
                state["filename"], state["content_type"])
    except BaseException:
        # BaseException: 也覆盖 ClientDisconnect 之外的 asyncio.CancelledError。
        pending.clear()
        try:
            out.close()
        except OSError:
            pass
        try:
            os.unlink(temp_path)
        except OSError:
            pass
        raise


def cleanup_stale_uploads(max_age_seconds: int = 6 * 3600) -> int:
    """删除异常退出 (进程被杀 / 断电) 时遗留在 data 目录的 .upload-* 半成品。"""
    removed = 0
    cutoff = time.time() - max_age_seconds
    for path in settings.data_dir.glob("*/.upload-*"):
        try:
            if path.is_file() and path.stat().st_mtime < cutoff:
                path.unlink()
                removed += 1
        except OSError:
            pass
    return removed


def save_text(text: str, stored_name: str):
    data = text.encode("utf-8")
    if len(data) > settings.max_text_bytes:
        raise ValueError("text too large")
    target_dir = shard_dir(stored_name)
    path = target_dir / stored_name
    with open(path, "wb") as f:
        f.write(data)
    return str(path.relative_to(settings.data_dir)), len(data), hashlib.sha256(data).hexdigest()


def safe_delete(rel_path: str | None):
    if not rel_path:
        return
    root = settings.data_dir.resolve()
    path = (root / rel_path).resolve()
    if root in path.parents and path.exists() and path.is_file():
        path.unlink()
