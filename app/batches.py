"""多文件上传: 每个文件仍走 resumable 的分块上传 (含续传与 SHA-256 校验), 收齐后先暂存,
整批收齐再打包成一个 zip 分享。

数据流::

    POST /api/batch/init            为每个文件建立 (或找回) 上传会话, 记下 batch_id + seq
    PUT  /api/upload/{upload_id}    分块上传 (与单文件完全相同; 会话属于批次时只暂存, 不建分享)
    POST /api/batch/{id}/complete   把暂存文件打包成 zip, 建一个文件分享, 删除暂存

批次与暂存文件保留 RESUME_HOURS 小时, 超时由 resumable.cleanup_stale 清掉。
"""
import hashlib
import logging
import os
import secrets
import zipfile

from fastapi import HTTPException

from .config import settings
from .database import connect
from .security import iso, utcnow
from .storage import safe_delete, shard_dir
from . import bundles, resumable

logger = logging.getLogger(__name__)

# 一个批次最多多少个文件 (前端也按这个数限制选择)
MAX_FILES = 50
# 同一个 IP 同时保留几个批次: 每个批次会占一批空会话/半成品文件, 不设上限容易被刷文件数
MAX_ACTIVE_PER_IP = 3
# 超过这个大小的文件不再尝试压缩 (视频/图片等本来压不动, 白耗 CPU)
_COMPRESS_MAX = 64 * 1024 * 1024
# 这些 MIME 已经是压缩格式, 直接 store
_STORED_MIME = ("video/", "audio/", "image/", "application/zip", "application/x-7z-compressed",
                "application/x-rar-compressed", "application/gzip", "application/x-gzip")
# zip 里不许出现的字符 (同时兼顾 Windows 解压)
_BAD_CHARS = {ord(c): "_" for c in '\\/:*?"<>|\r\n\t'}


def _drop_batch(batch_id: str):
    """丢掉整个批次 (会话、暂存文件和批次记录)。"""
    with connect() as conn:
        ids = [r["id"] for r in conn.execute("SELECT id FROM uploads WHERE batch_id=?", (batch_id,)).fetchall()]
    for upload_id in ids:
        resumable.discard(upload_id)  # 会在最后一个会话消失时顺手删掉批次记录
    with connect() as conn:
        conn.execute("DELETE FROM batches WHERE id=?", (batch_id,))


def _ensure_batch(batch_id: str | None, ip: str | None, api_key_id: int | None) -> str:
    """返回可用的批次 id: 传进来的 id 存在就复用 (整批续传), 否则新建。

    同一 IP 只保留最近 MAX_ACTIVE_PER_IP 个批次, 更早的整个丢掉。
    """
    now = iso(utcnow())
    with connect() as conn:
        if batch_id:
            if conn.execute("SELECT 1 FROM batches WHERE id=?", (batch_id,)).fetchone():
                conn.execute("UPDATE batches SET updated_at=? WHERE id=?", (now, batch_id))
                return batch_id
        new_id = secrets.token_hex(16)
        conn.execute("INSERT INTO batches(id,created_at,updated_at,ip,api_key_id) VALUES(?,?,?,?,?)",
                     (new_id, now, now, ip, api_key_id))
        stale = [r["id"] for r in conn.execute(
            "SELECT id FROM batches WHERE ip IS ? AND id<>? ORDER BY created_at DESC LIMIT -1 OFFSET ?",
            (ip, new_id, MAX_ACTIVE_PER_IP - 1)).fetchall()]
    for old in stale:
        _drop_batch(old)
    return new_id


def init_batch(files: list[dict], ip: str, api_key_id: int | None = None,
               batch_id: str | None = None) -> dict:
    """为批次里的每个文件建立 (或找回) 上传会话。files: [{sha256,size,filename,content_type}]"""
    if not files:
        raise HTTPException(400, "no files")
    if len(files) > MAX_FILES:
        raise HTTPException(400, f"at most {MAX_FILES} files per batch")
    total = sum(int(f["size"]) for f in files)
    limit = settings.max_upload_bytes
    if limit is not None and total > limit:
        raise HTTPException(413, "batch too large")
    batch_id = _ensure_batch(batch_id, ip, api_key_id)
    out = []
    for seq, f in enumerate(files):
        size = int(f["size"])
        upload_id, offset = resumable.open_session(
            f["sha256"], size, f.get("filename") or None, f.get("content_type"), ip,
            None, api_key_id, batch_id=batch_id, seq=seq)
        if size == 0 and not resumable.is_completed(upload_id):
            # 0 字节文件不会走到 receive_chunk, 建会话时直接标记收齐
            resumable.stage_empty(upload_id)
        out.append({"upload_id": upload_id, "offset": offset, "size": size,
                    "done": resumable.is_completed(upload_id)})
    return {"batch_id": batch_id, "files": out, "max_chunk": resumable.MAX_CHUNK_BYTES}


def staged_size(batch_id: str) -> tuple[int, int]:
    """批次里已收齐文件的字节数与会话数 (用于打包前的磁盘预检)。"""
    with connect() as conn:
        rows = conn.execute("SELECT size, completed FROM uploads WHERE batch_id=?", (batch_id,)).fetchall()
    return sum(int(r["size"] or 0) for r in rows if r["completed"]), len(rows)


def _arcname(name: str | None, used: set[str]) -> str:
    """zip 内的文件名: 去掉目录、非法字符, 同名时加 (2)、(3)…"""
    base = (name or "").replace("\\", "/").rsplit("/", 1)[-1]
    base = base.translate(_BAD_CHARS).strip().rstrip(". ")
    if base in ("", ".", ".."):
        base = "file"
    if len(base) > 180:
        stem, ext = os.path.splitext(base)
        base = stem[:160] + ext[:16]
    candidate, i = base, 2
    while candidate.lower() in used:
        stem, ext = os.path.splitext(base)
        candidate = f"{stem} ({i}){ext}"
        i += 1
    used.add(candidate.lower())
    return candidate


def _zip_name(rows, lang: str = "zh") -> str:
    """分享显示的名字: 首个文件名 + 个数, 例如「报告 等 3 个文件.zip」/「report (3 files).zip」。

    文件名会原样存进数据库并用于下载, 所以按创建时界面语言生成 (en / zh), 不在渲染时翻译。
    """
    n = len(rows)
    first = (rows[0]["filename"] or "").replace("\\", "/").rsplit("/", 1)[-1].strip()
    stem = os.path.splitext(first)[0].strip() if first else ""
    stem = stem.translate(_BAD_CHARS).strip().rstrip(". ")[:80]
    zh = lang != "en"
    if stem:
        return f"{stem} 等 {n} 个文件.zip" if zh else f"{stem} ({n} files).zip"
    return f"{n} 个文件.zip" if zh else f"{n} files.zip"


def _file_sha256(path) -> str:
    sha = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            sha.update(chunk)
    return sha.hexdigest()


def build_zip(batch_id: str, lang: str = "zh") -> dict:
    """把批次里暂存的文件打包成 zip (存到 data 目录), 返回新文件的信息。失败时不留临时文件。"""
    with connect() as conn:
        if not conn.execute("SELECT 1 FROM batches WHERE id=?", (batch_id,)).fetchone():
            raise HTTPException(404, "batch not found")
        rows = conn.execute("SELECT * FROM uploads WHERE batch_id=? ORDER BY seq", (batch_id,)).fetchall()
    if not rows:
        raise HTTPException(404, "batch not found")
    if len(rows) > MAX_FILES:
        raise HTTPException(400, "too many files")

    root = settings.data_dir.resolve()
    items, total = [], 0
    for r in rows:
        if not r["completed"] or not r["rel_path"]:
            raise HTTPException(409, f"file not uploaded yet: {r['filename'] or 'unnamed'}")
        path = (settings.data_dir / r["rel_path"]).resolve()
        if root not in path.parents or not path.is_file():
            raise HTTPException(409, "staged file missing")
        size = int(r["size"] or 0)
        total += size
        items.append((path, r["filename"], size, (r["content_type"] or "").lower()))

    tmp = settings.data_dir / f".zip-{secrets.token_hex(8)}"
    try:
        used: set[str] = set()
        entries = []  # zip 里的文件清单, 顺序与 zip 内一致 (分享页据此浏览, 见 bundles.py)
        with zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED, allowZip64=True) as zf:
            for path, name, size, mime in items:
                compress = zipfile.ZIP_STORED if (size > _COMPRESS_MAX or mime.startswith(_STORED_MIME)) \
                    else zipfile.ZIP_DEFLATED
                arcname = _arcname(name, used)
                zf.write(path, arcname=arcname, compress_type=compress)
                entries.append(bundles.describe(arcname, size, mime))
        sha = _file_sha256(tmp)
        stored_name = secrets.token_hex(16) + ".share"
        final = shard_dir(stored_name) / stored_name
        os.replace(tmp, final)
    except BaseException:
        try:
            tmp.unlink()
        except OSError:
            pass
        raise
    logger.info("batch %s packed: %d files, %d bytes -> %d bytes zip", batch_id, len(items), total, final.stat().st_size)
    return {"stored_name": stored_name,
            "rel_path": str(final.relative_to(settings.data_dir)),
            "size": final.stat().st_size,
            "sha256": sha,
            "filename": _zip_name(rows, lang),
            "count": len(items),
            "entries": entries,
            "bytes": total}


def finish(batch_id: str):
    """删除批次的暂存文件与记录 (zip 本身已移到正式位置, 由分享引用)。"""
    with connect() as conn:
        rows = conn.execute("SELECT rel_path FROM uploads WHERE batch_id=?", (batch_id,)).fetchall()
        conn.execute("DELETE FROM uploads WHERE batch_id=?", (batch_id,))
        conn.execute("DELETE FROM batches WHERE id=?", (batch_id,))
    for r in rows:
        safe_delete(r["rel_path"])
