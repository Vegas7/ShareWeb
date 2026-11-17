"""断点续传: 先建立上传会话, 再从头到尾按顺序分块追加。

浏览器先算出整个文件的 SHA-256, 用 (sha256, size) 建会话。上传中断后重新选择同一个文件时,
浏览器会重新算一遍哈希, 只有哈希和大小都与之前的会话一致才沿用它, 从服务器上已收到的字节处继续。
服务器边收边算 SHA-256, 收齐后与会话里的哈希核对, 不一致就丢弃 (文件在上传途中被改过之类)。
未完成的会话从最后一次写入起保留 RESUME_HOURS 小时。
"""
import asyncio
import hashlib
import logging
import os
import secrets
from datetime import timedelta
from pathlib import Path

from starlette.concurrency import run_in_threadpool

from .config import settings
from .database import connect
from .security import iso, utcnow
from .storage import DiskFull, UploadTooLarge, safe_delete, shard_dir, write_chunk
from . import app_settings

logger = logging.getLogger(__name__)

RESUME_HOURS = 24
MAX_CHUNK_BYTES = 64 * 1024 * 1024
MAX_SESSIONS_PER_IP = 20
_FLUSH_BYTES = 1024 * 1024


class UploadNotFound(LookupError):
    pass


class OffsetMismatch(ValueError):
    def __init__(self, offset: int):
        super().__init__(f"expected offset {offset}")
        self.offset = offset


class ChecksumMismatch(ValueError):
    pass


# 同一会话的请求串行处理 (客户端超时重发时, 上一个请求可能还在写); 单进程部署, asyncio 锁即可
_locks: dict[str, asyncio.Lock] = {}
# 已收部分的 SHA-256 中间状态: {upload_id: (已收字节数, hash 对象)}。进程重启后丢失, 届时从磁盘重算
_hashes: dict[str, tuple[int, "hashlib._Hash"]] = {}


def part_path(upload_id: str) -> Path:
    return shard_dir(upload_id) / f".part-{upload_id}"


def _part_size(path: Path) -> int | None:
    try:
        return path.stat().st_size
    except FileNotFoundError:
        return None


def _get(upload_id: str):
    with connect() as conn:
        return conn.execute("SELECT * FROM uploads WHERE id=?", (upload_id,)).fetchone()


def discard(upload_id: str):
    """删除上传会话: 未收齐的半成品、已暂存的文件和会话记录都不留。"""
    with connect() as conn:
        row = conn.execute("SELECT batch_id, rel_path FROM uploads WHERE id=?", (upload_id,)).fetchone()
        conn.execute("DELETE FROM uploads WHERE id=?", (upload_id,))
        if row and row["batch_id"]:
            # 批次里最后一个会话被丢掉时, 批次本身也没有存在的意义了
            left = conn.execute("SELECT 1 FROM uploads WHERE batch_id=? LIMIT 1", (row["batch_id"],)).fetchone()
            if not left:
                conn.execute("DELETE FROM batches WHERE id=?", (row["batch_id"],))
    _hashes.pop(upload_id, None)
    try:
        part_path(upload_id).unlink()
    except FileNotFoundError:
        pass
    if row and row["rel_path"]:
        safe_delete(row["rel_path"])


def is_completed(upload_id: str) -> bool:
    """会话是否已收齐 (多文件上传里表示文件已暂存, 可以打包了)。"""
    row = _get(upload_id)
    return bool(row and row["completed"])


def stage_empty(upload_id: str):
    """0 字节文件不会走到 receive_chunk, 建立会话时就直接标记为已收齐。"""
    _complete(upload_id, staged=True)


def open_session(sha256: str, size: int, filename: str, content_type: str | None, ip: str,
                 upload_id: str | None = None, api_key_id: int | None = None,
                 batch_id: str | None = None, seq: int | None = None) -> tuple[str, int]:
    """返回 (upload_id, 已收字节数)。upload_id 对应的会话与本次文件一致 (且是同一个 API 密钥 / 都来自网页) 时续传,
    否则新建会话。

    batch_id/seq 用于多文件上传: 同一批次里位置相同的会话按 (sha256, size) 认领, 实现整批续传。
    """
    now = iso(utcnow())
    row = None
    stale_id = None
    if upload_id:
        row = _get(upload_id)
    elif batch_id:
        with connect() as conn:
            row = conn.execute("SELECT * FROM uploads WHERE batch_id=? AND seq=?", (batch_id, seq)).fetchone()
        # 同一批次、同一位置上的文件被换成了另一个 (名字/大小相同但内容变了):
        # 先记下旧会话, 建好新会话后再删, 否则打包时两个版本都会被装进 zip。
        if row and not (row["sha256"] == sha256 and row["size"] == size
                        and row["api_key_id"] == api_key_id and (row["batch_id"] or None) == batch_id):
            stale_id = row["id"]
            row = None
    if (row and row["sha256"] == sha256 and row["size"] == size and row["api_key_id"] == api_key_id
            and (row["batch_id"] or None) == (batch_id or None)):
        if row["completed"]:
            return row["id"], size
        path = part_path(row["id"])
        offset = _part_size(path)
        if offset is None or offset > size:
            open(path, "wb").close()
            offset = 0
        with connect() as conn:
            conn.execute("UPDATE uploads SET filename=?, content_type=?, ip=?, updated_at=? WHERE id=?",
                         (filename, content_type, ip, now, row["id"]))
        return row["id"], offset

    new_id = secrets.token_hex(16)
    open(part_path(new_id), "xb").close()
    with connect() as conn:
        conn.execute("INSERT INTO uploads (id, sha256, size, filename, content_type, ip, created_at, updated_at, "
                     "api_key_id, batch_id, seq) VALUES (?,?,?,?,?,?,?,?,?,?,?)",
                     (new_id, sha256, size, filename, content_type, ip, now, now, api_key_id, batch_id, seq))
        # 每个 IP 最多保留若干个未完成的单文件会话, 多出来的从最久没动的开始丢弃
        # (多文件批次的会话不受这个上限约束, 否则 50 个文件的批次会把自己的会话挤掉)
        extra = conn.execute("SELECT id FROM uploads WHERE ip=? AND batch_id IS NULL ORDER BY updated_at DESC "
                             "LIMIT -1 OFFSET ?", (ip, MAX_SESSIONS_PER_IP)).fetchall()
    for r in extra:
        if not (_locks.get(r["id"]) and _locks[r["id"]].locked()):
            discard(r["id"])
    if stale_id and not (_locks.get(stale_id) and _locks[stale_id].locked()):
        discard(stale_id)
    return new_id, 0


def _hash_prefix(path: Path, length: int):
    sha = hashlib.sha256()
    with open(path, "rb") as f:
        left = length
        while left > 0:
            block = f.read(min(left, 4 * 1024 * 1024))
            if not block:
                break
            sha.update(block)
            left -= len(block)
    return sha


def _truncate(path: Path, length: int):
    try:
        os.truncate(path, length)
    except OSError:
        pass


def _touch(upload_id: str):
    with connect() as conn:
        conn.execute("UPDATE uploads SET updated_at=? WHERE id=?", (iso(utcnow()), upload_id))


def _complete(upload_id: str, staged: bool = False) -> tuple[str, str]:
    """把收齐的文件移到正式位置并返回 (stored_name, rel_path)。

    staged=True 时保留 uploads 行 (completed=1, 记下 stored_name/rel_path), 文件先暂存,
    等多文件上传整批打包后再删; 否则删除会话 (单文件上传立即建分享)。
    """
    path = part_path(upload_id)
    with open(path, "rb+") as f:
        os.fsync(f.fileno())
    stored_name = secrets.token_hex(16) + ".share"
    final = shard_dir(stored_name) / stored_name
    os.replace(path, final)
    rel_path = str(final.relative_to(settings.data_dir))
    with connect() as conn:
        if staged:
            conn.execute("UPDATE uploads SET completed=1, stored_name=?, rel_path=?, updated_at=? WHERE id=?",
                         (stored_name, rel_path, iso(utcnow()), upload_id))
        else:
            conn.execute("DELETE FROM uploads WHERE id=?", (upload_id,))
    return stored_name, rel_path


async def receive_chunk(upload_id: str, offset: int, stream, on_disk_full=None, api_key_id: int | None = None):
    """把请求体追加到会话的 offset 处 (必须正好等于已收字节数)。

    会话只接受建立它的一方继续上传: 网页建的 (api_key_id 为 None) 或同一个 API 密钥, 否则视为不存在。

    返回 (row, 新的已收字节数, done)。done 时 done = (stored_name, rel_path), 文件已校验并移到正式位置。
    中途失败 (断开 / 超限 / 磁盘满) 时把文件截回 offset, 下次从这里重新发这一块。
    """
    lock = _locks.setdefault(upload_id, asyncio.Lock())
    async with lock:
        row = await run_in_threadpool(_get, upload_id)
        if row and row["api_key_id"] != api_key_id:
            raise UploadNotFound(upload_id)
        path = part_path(upload_id)
        current = _part_size(path) if row else None
        if current is None:
            if row:
                await run_in_threadpool(discard, upload_id)
            _locks.pop(upload_id, None)
            raise UploadNotFound(upload_id)
        if offset != current:
            raise OffsetMismatch(current)

        size = row["size"]
        state = _hashes.pop(upload_id, None)
        sha = state[1] if state and state[0] == current else await run_in_threadpool(_hash_prefix, path, current)
        received = 0
        pending: list[bytes] = []
        pending_len = 0
        out = open(path, "r+b")
        out.seek(current)

        async def flush():
            nonlocal pending_len
            data = b"".join(pending)
            pending.clear()
            pending_len = 0
            if app_settings.upload_capacity_bytes() < len(data):
                need = size - (current + received) + len(data)  # 本块剩下的加上之后的都要放得下
                if not (on_disk_full and await run_in_threadpool(on_disk_full, need)):
                    raise DiskFull("not enough disk space")
            await run_in_threadpool(write_chunk, out, sha, data)

        try:
            async for chunk in stream:
                if not chunk:
                    continue
                received += len(chunk)
                if received > MAX_CHUNK_BYTES or current + received > size:
                    raise UploadTooLarge("chunk too large")
                pending.append(chunk)
                pending_len += len(chunk)
                if pending_len >= _FLUSH_BYTES:
                    await flush()
            if pending:
                await flush()
            await run_in_threadpool(out.close)
        except BaseException:
            pending.clear()
            out.close()
            _truncate(path, current)
            raise

        total = current + received
        if total < size:
            _hashes[upload_id] = (total, sha)
            await run_in_threadpool(_touch, upload_id)
            return row, total, None
        _locks.pop(upload_id, None)
        if sha.hexdigest() != row["sha256"]:
            await run_in_threadpool(discard, upload_id)
            raise ChecksumMismatch(upload_id)
        return row, total, await run_in_threadpool(_complete, upload_id, bool(row["batch_id"]))


def cleanup_stale(hours: int = RESUME_HOURS) -> int:
    """删除超过保留时间没有动静的未完成会话, 以及没有会话记录的 .part-* 文件。"""
    cutoff = iso(utcnow() - timedelta(hours=hours))
    with connect() as conn:
        ids = [r["id"] for r in conn.execute("SELECT id FROM uploads WHERE updated_at<?", (cutoff,))]
        live = {r["id"] for r in conn.execute("SELECT id FROM uploads")}
    removed = 0
    for upload_id in ids:
        if _locks.get(upload_id) and _locks[upload_id].locked():
            continue
        discard(upload_id)
        _locks.pop(upload_id, None)
        removed += 1
    orphan_cutoff = utcnow().timestamp() - 3600
    for path in settings.data_dir.glob("*/.part-*"):
        if path.name[len(".part-"):] in live:
            continue
        try:
            if path.stat().st_mtime < orphan_cutoff:
                path.unlink()
                removed += 1
        except OSError:
            pass
    # 多文件上传: 没有会话的批次记录, 以及打包中途崩溃留下的 zip 临时文件
    with connect() as conn:
        conn.execute("DELETE FROM batches WHERE updated_at<? AND id NOT IN "
                     "(SELECT batch_id FROM uploads WHERE batch_id IS NOT NULL)", (cutoff,))
    for path in settings.data_dir.glob(".zip-*"):
        try:
            if path.is_file() and path.stat().st_mtime < orphan_cutoff:
                path.unlink()
                removed += 1
        except OSError:
            pass
    return removed
