"""外部 API (/api/v1), 供脚本 / 其他程序调用。使用说明见管理后台的「API」页 (web/static/js/admin.js)。

所有接口都要带 API 密钥 (管理后台创建): Authorization: Bearer <密钥>, 或 X-API-Key: <密钥>。
IP 黑名单、提取码输错冷却 / 拉黑等规则与网页相同。下载文件用分享里的 download_url (/download/<token>), 不需要密钥。
"""
import logging
import secrets
from dataclasses import dataclass
from typing import Optional

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query, Request, Response
from fastapi.responses import JSONResponse, PlainTextResponse
from pydantic import BaseModel, Field
from starlette.concurrency import run_in_threadpool
from starlette.requests import ClientDisconnect

from .config import settings
from .deps import ensure_not_blacklisted
from .services import (SPECIAL_CODE, RedeemBlocked, create_share_text, delete_key_share, get_active_file_by_sha256,
                       get_share_by_token, list_key_shares, log_event, redeem_code)
from .shareops import create_file_share, disk_full_handler, ensure_space, share_url
from .storage import BadUpload, DiskFull, UploadTooLarge, save_text, save_upload_stream
from . import apikeys, llm_doc, resumable

logger = logging.getLogger(__name__)


@dataclass
class Caller:
    key_id: int
    key_name: str
    ip: str


async def require_key(request: Request) -> Caller:
    ip = ensure_not_blacklisted(request)
    auth = request.headers.get("authorization", "")
    key = auth[7:].strip() if auth[:7].lower() == "bearer " else request.headers.get("x-api-key", "").strip()
    row = await run_in_threadpool(apikeys.authenticate, key, ip)
    if not row:
        log_event(ip, "API_AUTH", "FAIL", detail=f"PATH={request.url.path}",
                  user_agent=request.headers.get("user-agent", "-"), level=logging.WARNING)
        raise HTTPException(401, "invalid or missing API key", headers={"WWW-Authenticate": "Bearer"})
    return Caller(row["id"], row["name"], ip)


# 路由级别统一校验密钥; 各接口再声明 Depends(require_key) 取调用方 (同一请求内只校验一次)
router = APIRouter(prefix="/api/v1", dependencies=[Depends(require_key)])


class UploadInit(BaseModel):
    sha256: str = Field(pattern=r"^[0-9a-fA-F]{64}$")
    size: int = Field(ge=0)
    filename: str = Field(default="", max_length=4096)
    content_type: Optional[str] = Field(default=None, max_length=200)
    upload_id: Optional[str] = Field(default=None, pattern=r"^[0-9a-f]{32}$")


class TextIn(BaseModel):
    text: str = Field(min_length=1)


def _share(row, caller: Caller, with_text: bool = False) -> dict:
    """统一的分享对象。with_text 时文本分享附上正文。"""
    is_file = row["type"] == "file"
    d = {
        "token": row["token"], "code": row["code"], "type": row["type"], "filename": row["original_name"],
        "size": row["size"], "sha256": row["sha256"], "mime_type": row["mime_type"],
        "created_at": row["created_at"], "expires_at": None if row["locked"] else row["expires_at"],
        "locked": bool(row["locked"]), "download_count": row["download_count"],
        "url": share_url(row["token"]),
        "download_url": f"{settings.public_base_url}/download/{row['token']}" if is_file else None,
        "owned": row["api_key_id"] == caller.key_id,
    }
    if with_text and not is_file:
        try:
            d["text"] = (settings.data_dir / row["storage_path"]).read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            raise HTTPException(404, "text content missing")
    return d


def _created(token: str, caller: Caller) -> dict:
    row = get_share_by_token(token)
    if not row:
        raise HTTPException(500, "share vanished right after creation")
    return _share(row, caller)


@router.get("/info")
async def info(caller: Caller = Depends(require_key)):
    return {"max_upload_bytes": settings.max_upload_bytes, "max_text_bytes": settings.max_text_bytes,
            "retention_days": settings.retention_days, "max_chunk_bytes": resumable.MAX_CHUNK_BYTES,
            "key": {"id": caller.key_id, "name": caller.key_name}}


@router.get("/llms.txt", response_class=PlainTextResponse)
async def llms_txt():
    """给 AI agent 看的 API 说明 (Markdown), 与管理后台「API」页里的「给 AI 看的版本」相同。"""
    return PlainTextResponse(llm_doc.render(), media_type="text/markdown; charset=utf-8")


@router.post("/files", status_code=201)
async def upload_file(request: Request, background: BackgroundTasks, caller: Caller = Depends(require_key)):
    """一次性上传 (multipart/form-data, 字段名 file)。大文件建议用下面的断点续传。"""
    try:
        length = int(request.headers.get("content-length") or 0)
    except ValueError:
        length = 0
    limit = settings.max_upload_bytes
    if limit is not None and length > limit + 4 * 1024 * 1024:
        raise HTTPException(413, "file too large")
    await ensure_space(length, caller.ip)
    stored_name = secrets.token_hex(16) + ".share"
    try:
        rel_path, size, sha, filename, content_type = await save_upload_stream(
            request, stored_name, on_disk_full=disk_full_handler(caller.ip))
    except UploadTooLarge:
        raise HTTPException(413, "file too large")
    except DiskFull:
        raise HTTPException(507, "not enough disk space on server")
    except BadUpload as exc:
        raise HTTPException(400, f"bad upload: {exc}")
    except ClientDisconnect:
        return Response(status_code=400)
    created = create_file_share(request, background, filename, content_type, size, sha, stored_name, rel_path,
                                caller.ip, caller.key_id)
    return _created(created["token"], caller)


@router.post("/uploads")
async def upload_init(payload: UploadInit, caller: Caller = Depends(require_key)):
    """断点续传第一步。服务器上已有相同文件 (SHA-256 一致) 时直接返回那个分享, 不用再传。"""
    sha = payload.sha256.lower()
    row = await run_in_threadpool(get_active_file_by_sha256, sha)
    if row:
        return {"exists": True, "share": _share(row, caller)}
    limit = settings.max_upload_bytes
    if limit is not None and payload.size > limit:
        raise HTTPException(413, "file too large")
    upload_id, offset = await run_in_threadpool(
        resumable.open_session, sha, payload.size, payload.filename or None, payload.content_type, caller.ip,
        payload.upload_id, caller.key_id)
    await ensure_space(payload.size - offset, caller.ip)
    return {"exists": False, "upload_id": upload_id, "offset": offset, "max_chunk": resumable.MAX_CHUNK_BYTES}


@router.put("/uploads/{upload_id}")
async def upload_chunk(upload_id: str, request: Request, background: BackgroundTasks,
                       offset: int = Query(ge=0), caller: Caller = Depends(require_key)):
    """断点续传第二步: 请求体是文件从 offset 开始的一段。最后一段收齐后校验 SHA-256 并返回分享。"""
    if len(upload_id) != 32 or any(c not in "0123456789abcdef" for c in upload_id):
        raise HTTPException(404, "upload not found")
    try:
        row, received, done = await resumable.receive_chunk(
            upload_id, offset, request.stream(), disk_full_handler(caller.ip), caller.key_id)
    except resumable.UploadNotFound:
        raise HTTPException(404, "upload not found")
    except resumable.OffsetMismatch as exc:
        return JSONResponse({"detail": "offset mismatch", "offset": exc.offset}, status_code=409)
    except resumable.ChecksumMismatch:
        log_event(caller.ip, "UPLOAD", "CHECKSUM_MISMATCH", detail=f"ID={upload_id} API_KEY={caller.key_id}",
                  level=logging.WARNING)
        raise HTTPException(422, "checksum mismatch")
    except UploadTooLarge:
        raise HTTPException(413, "chunk too large")
    except DiskFull:
        raise HTTPException(507, "not enough disk space on server")
    except ClientDisconnect:
        return Response(status_code=400)
    if not done:
        return {"done": False, "offset": received}
    stored_name, rel_path = done
    created = create_file_share(request, background, row["filename"], row["content_type"], received, row["sha256"],
                                stored_name, rel_path, caller.ip, caller.key_id)
    return {"done": True, "share": _created(created["token"], caller)}


@router.post("/texts", status_code=201)
async def create_text(request: Request, payload: TextIn, caller: Caller = Depends(require_key)):
    stored_name = secrets.token_hex(16) + ".share"
    try:
        rel_path, size, sha = save_text(payload.text, stored_name)
    except ValueError:
        raise HTTPException(413, "text too large")
    _, token, _, _ = create_share_text(stored_name, rel_path, size, sha, caller.ip,
                                       request.headers.get("user-agent", "-"), caller.key_id)
    return _created(token, caller)


@router.get("/shares")
async def my_shares(limit: int = Query(100, ge=1, le=1000), offset: int = Query(0, ge=0),
                    caller: Caller = Depends(require_key)):
    """这个密钥创建的、仍然有效的分享 (新的在前)。"""
    rows, total = await run_in_threadpool(list_key_shares, caller.key_id, limit, offset)
    return {"total": total, "limit": limit, "offset": offset, "items": [_share(r, caller) for r in rows]}


@router.get("/shares/{token}")
async def get_share(token: str, caller: Caller = Depends(require_key)):
    row = get_share_by_token(token) if 0 < len(token) <= 64 else None
    if not row:
        raise HTTPException(404, "share not found or expired")
    return _share(row, caller, with_text=True)


@router.delete("/shares/{token}", status_code=204)
async def delete_share(token: str, caller: Caller = Depends(require_key)):
    """只能删除这个密钥自己创建的分享; 管理员锁定的分享不能删除。"""
    result = await run_in_threadpool(delete_key_share, token, caller.key_id) if 0 < len(token) <= 64 else "not_found"
    if result == "not_found":
        raise HTTPException(404, "share not found, expired, or not created by this key")
    if result == "locked":
        raise HTTPException(409, "share is locked by the admin")
    log_event(caller.ip, "API_DELETE", "SUCCESS", detail=f"TOKEN={token[:8]}… API_KEY={caller.key_id}")
    return Response(status_code=204)


@router.get("/codes/{code}")
async def lookup_code(code: str, request: Request, caller: Caller = Depends(require_key)):
    """按 4 位提取码查分享。输错次数与网页共用同一套限制 (按 IP: 连错冷却, 再错拉黑)。"""
    if len(code) != 4 or not code.isdigit():
        raise HTTPException(422, "code must be 4 digits")
    if code == SPECIAL_CODE:
        return JSONResponse({"detail": "invalid code"}, status_code=404)
    try:
        row, fail_count, blacklisted = await run_in_threadpool(
            redeem_code, code, caller.ip, request.headers.get("user-agent", "-"))
    except RedeemBlocked as exc:
        if exc.cooldown_until:
            return JSONResponse({"detail": "too many wrong codes, try again later", "cooldown_until": exc.cooldown_until},
                                status_code=429)
        raise HTTPException(403, "IP blacklisted")
    if blacklisted:
        raise HTTPException(403, "IP blacklisted")
    if row is None:
        return JSONResponse({"detail": "invalid code", "fail_count": fail_count}, status_code=404)
    return _share(row, caller, with_text=True)
