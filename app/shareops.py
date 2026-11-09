"""网页接口 (main.py) 与外部 API (api_v1.py) 共用的上传 / 分享辅助函数。"""
import mimetypes
from pathlib import Path

from fastapi import HTTPException
from starlette.concurrency import run_in_threadpool

from .config import settings
from .services import create_share_file, evict_for_space, mirror_to_github
from . import app_settings, github_mirror


def share_url(token: str) -> str:
    return f"{settings.public_base_url}/share/{token}"


def share_payload(row) -> dict:
    return {"token": row["token"], "code": row["code"], "filename": row["original_name"], "size": row["size"],
            "sha256": row["sha256"], "expires_at": None if row["locked"] else row["expires_at"],
            "url": share_url(row["token"])}


async def ensure_space(need: int, ip: str):
    """磁盘放不下 need 字节时 (开启「自动清理」则先删最旧的文件腾空间) 返回 507。"""
    if need > app_settings.upload_capacity_bytes():
        if not (settings.auto_evict and await run_in_threadpool(evict_for_space, need, app_settings.upload_capacity_bytes, ip)):
            raise HTTPException(507, "not enough disk space on server")


def disk_full_handler(ip: str):
    return (lambda need: evict_for_space(need, app_settings.upload_capacity_bytes, ip)) if settings.auto_evict else None


def create_file_share(request, background, filename, content_type, size, sha, stored_name, rel_path, ip,
                      api_key_id=None) -> dict:
    # 浏览器对 .mov 等常报空/通用 MIME，按扩展名补正，保证前端能识别为视频。
    mime = content_type or ""
    if not mime or mime == "application/octet-stream":
        guessed, _ = mimetypes.guess_type(filename or "")
        mime = guessed or "application/octet-stream"
    filename = filename or "download.bin"
    share_id, token, code, expires_at = create_share_file(
        filename, mime, size, sha, stored_name, rel_path, ip, request.headers.get("user-agent", "-"), api_key_id)
    if github_mirror.enabled() and github_mirror.fits(size):
        # 后台镜像到 GitHub 私仓，不阻塞上传响应。
        background.add_task(mirror_to_github, share_id)
    return {"ok": True, "id": share_id, "token": token, "code": code, "filename": filename, "size": size, "sha256": sha,
            "expires_at": expires_at, "url": share_url(token)}


def resolve_share_path(row) -> Path:
    """校验 storage_path 落在 data 目录内并存在, 返回绝对路径。"""
    abs_path = (settings.data_dir / Path(row["storage_path"])).resolve()
    root = settings.data_dir.resolve()
    if root not in abs_path.parents or not abs_path.is_file():
        raise HTTPException(404, "file missing")
    return abs_path
