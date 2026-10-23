import asyncio
import ipaddress
import logging
import mimetypes
import secrets
from contextlib import asynccontextmanager
from datetime import datetime, time, timedelta, timezone
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, BackgroundTasks, Cookie, Depends, FastAPI, Form, HTTPException, Request, Response
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from starlette.concurrency import run_in_threadpool
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import ClientDisconnect

from .config import settings
from .database import init_db, connect
from .deps import client_ip, ensure_not_blacklisted
from .logging_config import setup_logging
from .security import utcnow, iso, require_admin_session
from .services import (SPECIAL_CODE, RedeemBlocked, cleanup_expired, cleanup_old_files, create_share_file, create_share_text,
                       delete_files, evict_for_space, evictable_files, get_active_file_by_sha256, get_github_download_url,
                       get_share_by_token, list_files, log_event, mirror_to_github, redeem_code, set_files_locked, share_status,
                       touch_download)
from .storage import save_upload_stream, save_text, cleanup_stale_uploads, UploadTooLarge, BadUpload, DiskFull
from . import crypto
from . import github_mirror
from . import geoip, visitors
from . import app_settings

setup_logging()
logger = logging.getLogger(__name__)


async def cleanup_loop():
    # 都放进线程池: 清理过期文件可能要删 GitHub 镜像 (走网络), 直接调用会卡住整个事件循环
    while True:
        try:
            await run_in_threadpool(cleanup_expired)
        except Exception:
            logger.exception("cleanup failed")
        try:
            pruned = await run_in_threadpool(visitors.prune, settings.visitor_retention_days)
            if pruned:
                logger.info("pruned %d old visitor records", pruned)
        except Exception:
            logger.exception("visitor prune failed")
        try:
            stale = await run_in_threadpool(cleanup_stale_uploads)
            if stale:
                logger.info("removed %d stale partial uploads", stale)
        except Exception:
            logger.exception("stale upload cleanup failed")
        await asyncio.sleep(3600)


async def visitor_flush_loop():
    while True:
        await asyncio.sleep(5)
        try:
            await run_in_threadpool(visitors.flush)
        except Exception:
            logger.exception("visitor flush failed")


@asynccontextmanager
async def lifespan(app: FastAPI):
    for p in (settings.data_dir, settings.log_dir, settings.database_dir):
        p.mkdir(parents=True, exist_ok=True)
    init_db()
    app_settings.load()
    task = asyncio.create_task(cleanup_loop())
    flusher = asyncio.create_task(visitor_flush_loop())
    try:
        yield
    finally:
        for t in (task, flusher):
            t.cancel()
            try:
                await t
            except asyncio.CancelledError:
                pass
        try:
            visitors.flush()  # 退出前把内存里还没写入的访客记录存下来
        except Exception:
            logger.exception("final visitor flush failed")


app = FastAPI(title="ShareWeb", docs_url=None, redoc_url=None, lifespan=lifespan)

class NoCacheHTMLMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        # 记录访客 IP (只计页面和接口请求; 不含查询参数, 以免把分享链接里的参数之类记下来)
        if visitors.should_record(request.url.path):
            visitors.record(client_ip(request), request.url.path, request.headers.get("user-agent"))
        response = await call_next(request)
        if request.url.path in ("/", "/admin", "/special") or request.url.path.startswith("/share/"):
            response.headers["Cache-Control"] = "no-store"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "same-origin"
        response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
        return response

app.add_middleware(NoCacheHTMLMiddleware)
app.mount("/static", StaticFiles(directory=settings.web_dir / "static"), name="static")

class RedeemRequest(BaseModel):
    code: str = Field(pattern=r"^\d{4}$")

class ShareStatusRequest(BaseModel):
    tokens: list[str] = Field(max_length=200)

class TextShareRequest(BaseModel):
    text: str = Field(min_length=1)

class AdminLoginRequest(BaseModel):
    password: str

class AdminCleanupRequest(BaseModel):
    days: Optional[int] = Field(default=None)

class AdminIpsRequest(BaseModel):
    ips: list[str] = Field(min_length=1, max_length=1000)
    reason: Optional[str] = Field(default=None, max_length=200)

class AdminDeleteFilesRequest(BaseModel):
    ids: list[int] = Field(min_length=1, max_length=1000)

class AdminLockFilesRequest(BaseModel):
    ids: list[int] = Field(min_length=1, max_length=1000)
    locked: bool

class AdminSettingsRequest(BaseModel):
    # 只修改传了的字段。单文件上限 (MB); 0 = 不限制 (仍受磁盘剩余空间约束)
    max_upload_mb: Optional[int] = Field(default=None, ge=0, le=app_settings.MAX_UPLOAD_MB_CAP)
    # 磁盘不足时自动删除最旧的文件
    auto_evict: Optional[bool] = None

@app.get("/", response_class=HTMLResponse)
async def index():
    return (settings.web_dir / "index.html").read_text(encoding="utf-8")

@app.get("/share/{token}", response_class=HTMLResponse)
async def share_page(token: str, request: Request):
    ip = ensure_not_blacklisted(request)
    row = get_share_by_token(token)
    if not row:
        log_event(ip, "OPEN_SHARE", "NOT_FOUND", detail="TOKEN_INVALID_OR_EXPIRED", user_agent=request.headers.get("user-agent","-"), level=logging.WARNING)
        return HTMLResponse((settings.web_dir / "expired.html").read_text(encoding="utf-8"), status_code=410)
    log_event(ip, "OPEN_SHARE", "SUCCESS", row["id"], f"TYPE={row['type']}", request.headers.get("user-agent","-"))
    return (settings.web_dir / "share.html").read_text(encoding="utf-8")

@app.get("/admin", response_class=HTMLResponse)
async def admin_page():
    return (settings.web_dir / "admin.html").read_text(encoding="utf-8")

@app.get("/api/config")
async def public_config():
    """首页展示上传限制、上传前预检文件大小用。"""
    return {"max_upload_bytes": settings.max_upload_bytes, "max_text_bytes": settings.max_text_bytes,
            "retention_days": settings.retention_days}

@app.post("/api/share-status")
async def share_status_api(request: Request, payload: ShareStatusRequest):
    """首页本地历史标注「已删除 / 已过期」用; 只返回状态, 不返回任何内容。"""
    ensure_not_blacklisted(request)
    tokens = [t for t in payload.tokens if isinstance(t, str) and 0 < len(t) <= 64]
    return {"status": await run_in_threadpool(share_status, tokens)}

@app.post("/api/check-hash")
async def check_hash(request: Request, sha256: str = Form(...)):
    ensure_not_blacklisted(request)
    normalized = sha256.strip().lower()
    if len(normalized) != 64 or any(c not in "0123456789abcdef" for c in normalized):
        raise HTTPException(400, "invalid sha256")
    row = get_active_file_by_sha256(normalized)
    if not row:
        return {"exists": False}
    return {
        "exists": True,
        "token": row["token"],
        "code": row["code"],
        "filename": row["original_name"],
        "size": row["size"],
        "sha256": row["sha256"],
        "expires_at": None if row["locked"] else row["expires_at"],
        "url": f"{settings.public_base_url}/share/{row['token']}",
    }

@app.post("/api/upload")
async def upload_file(request: Request, background: BackgroundTasks):
    ip = ensure_not_blacklisted(request)
    if request.headers.get("content-length"):
        try:
            length = int(request.headers["content-length"])
        except ValueError:
            length = None
        if length is not None:
            limit = settings.max_upload_bytes
            if limit is not None and length > limit + 4*1024*1024:
                raise HTTPException(413, "file too large")
            if length > app_settings.upload_capacity_bytes():
                # 开启「自动清理」时先删最旧的文件腾空间, 腾不出来才拒绝
                if not (settings.auto_evict and await run_in_threadpool(evict_for_space, length, app_settings.upload_capacity_bytes, ip)):
                    raise HTTPException(507, "not enough disk space on server")
    stored_name = secrets.token_hex(16) + ".share"
    try:
        # 流式写入 data 目录, 不经过 /tmp; 失败/断开时半成品会被删除。
        on_full = (lambda need: evict_for_space(need, app_settings.upload_capacity_bytes, ip)) if settings.auto_evict else None
        rel_path, size, sha, filename, content_type = await save_upload_stream(request, stored_name, on_disk_full=on_full)
    except UploadTooLarge:
        raise HTTPException(413, "file too large")
    except DiskFull:
        logger.warning("upload aborted: disk almost full ip=%s", ip)
        raise HTTPException(507, "not enough disk space on server")
    except BadUpload as exc:
        raise HTTPException(400, f"bad upload: {exc}")
    except ClientDisconnect:
        logger.info("upload aborted by client ip=%s", ip)
        return Response(status_code=400)
    except Exception:
        logger.exception("upload save failed")
        raise HTTPException(500, "upload failed")
    # 浏览器对 .mov 等常报空/通用 MIME，按扩展名补正，保证前端能识别为视频。
    mime = content_type or ""
    if not mime or mime == "application/octet-stream":
        guessed, _ = mimetypes.guess_type(filename or "")
        mime = guessed or "application/octet-stream"
    share_id, token, code, expires_at = create_share_file(
        filename or "download.bin", mime, size, sha, stored_name, rel_path, ip, request.headers.get("user-agent","-"))
    if github_mirror.enabled() and github_mirror.fits(size):
        # 后台镜像到 GitHub 私仓，不阻塞上传响应。
        background.add_task(mirror_to_github, share_id)
    return {"ok": True, "id": share_id, "token": token, "code": code, "filename": filename or "download.bin", "size": size, "sha256": sha, "expires_at": expires_at, "url": f"{settings.public_base_url}/share/{token}"}

@app.post("/api/text")
async def upload_text(request: Request, payload: TextShareRequest):
    ip = ensure_not_blacklisted(request)
    stored_name = secrets.token_hex(16) + ".share"
    try:
        rel_path, size, sha = save_text(payload.text, stored_name)
    except ValueError:
        raise HTTPException(413, "text too large")
    share_id, token, code, expires_at = create_share_text(stored_name, rel_path, size, sha, ip, request.headers.get("user-agent","-"))
    return {"ok": True, "id": share_id, "token": token, "code": code, "filename": "text.txt", "size": size, "sha256": sha, "expires_at": expires_at, "url": f"{settings.public_base_url}/share/{token}"}

@app.get("/api/share/{token}")
async def share_meta(token: str, request: Request):
    ensure_not_blacklisted(request)
    row = get_share_by_token(token)
    if not row:
        raise HTTPException(404, "share not found or expired")
    text = None
    if row["type"] == "text":
        try:
            text = (settings.data_dir / row["storage_path"]).read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            raise HTTPException(404, "text content missing")
    # 密钥对持有分享链接的人可见 (加密下载的授权对象即链接持有者)。
    enc_key = row["enc_key"] if row["type"] == "file" else None
    github_available = github_mirror.enabled() and row["type"] == "file" and github_mirror.fits(row["size"] or 0)
    return {"token": row["token"], "type": row["type"], "filename": row["original_name"], "size": row["size"], "sha256": row["sha256"], "mime_type": row["mime_type"], "text": text, "created_at": row["created_at"], "expires_at": None if row["locked"] else row["expires_at"], "download_count": row["download_count"], "enc_key": enc_key, "github": github_available}


@app.get("/api/share/{token}/github")
async def share_github_url(token: str, request: Request):
    """返回该文件的 GitHub 短时效下载直链 (token 不外泄，仅返回临时链接) 及下载后的文件名。"""
    ip = ensure_not_blacklisted(request)
    if not github_mirror.enabled():
        raise HTTPException(404, "github mirror not configured")
    row = get_share_by_token(token)
    if not row or row["type"] != "file":
        raise HTTPException(404, "file not found or expired")
    if not github_mirror.fits(row["size"] or 0):
        raise HTTPException(413, "file too large for github mirror")
    # 未镜像时这里会同步上传到 GitHub, 放进线程池以免卡住整个事件循环。
    link = await run_in_threadpool(get_github_download_url, row["id"])
    if not link:
        raise HTTPException(503, "github mirror not ready, please retry")
    log_event(ip, "GITHUB_LINK", "SUCCESS", row["id"], "", request.headers.get("user-agent", "-"))
    # filename: 通过该链接下载后的实际文件名 (大文件走 Release 时 GitHub 会去掉中文等字符)。
    return {"url": link["url"], "filename": link["filename"]}

@app.post("/api/redeem")
async def redeem(request: Request, payload: RedeemRequest):
    ip = client_ip(request)
    ua = request.headers.get("user-agent", "-")
    if payload.code == SPECIAL_CODE:
        # 0000 是使用说明页的入口, 不计失败次数
        log_event(ip, "REDEEM_SPECIAL", "SUCCESS", detail=f"CODE={SPECIAL_CODE}", user_agent=ua)
        return {"ok": True, "special": True}
    try:
        row, fail_count, blacklisted = redeem_code(payload.code, ip, ua)
    except RedeemBlocked as exc:
        if exc.cooldown_until:
            return JSONResponse({"ok": False, "error": "cooldown", "cooldown_until": exc.cooldown_until}, status_code=429)
        raise HTTPException(403, "IP blacklisted")
    if blacklisted:
        raise HTTPException(403, "IP blacklisted")
    if row is None:
        return JSONResponse({"ok": False, "error": "invalid_code", "fail_count": fail_count}, status_code=404)
    return {"ok": True, "token": row["token"], "url": f"/share/{row['token']}"}

def _resolve_share_path(row) -> Path:
    """校验 storage_path 落在 data 目录内并存在, 返回绝对路径。"""
    abs_path = (settings.data_dir / Path(row["storage_path"])).resolve()
    root = settings.data_dir.resolve()
    if root not in abs_path.parents or not abs_path.is_file():
        raise HTTPException(404, "file missing")
    return abs_path


@app.get("/download/{token}")
async def download(token: str, request: Request, enc: int = 0, inline: int = 0):
    """明文下载 (FastAPI 直出, 原生支持 Range/断点续传)。

    带 ?enc=1 时返回 AES-256-CBC 加密的不可识别 .dat 混淆块。
    带 ?inline=1 时以 inline 方式返回 (供 <video>/<audio> 在线播放, 不计下载次数)。
    """
    ip = ensure_not_blacklisted(request)
    row = get_share_by_token(token)
    if not row or row["type"] != "file":
        raise HTTPException(404, "file not found or expired")
    abs_path = _resolve_share_path(row)

    if inline and not enc:
        # 在线播放/预览: inline 返回, 支持 Range; 播放会产生大量分段请求, 故不计入下载次数。
        # MOV/M4V 与 MP4 同为 ISO BMFF, 用 video/mp4 发送可让 Chrome 播放其中的 H.264。
        mime = (row["mime_type"] or "")
        if not mime or mime == "application/octet-stream":
            guessed, _ = mimetypes.guess_type(row["original_name"] or "")
            mime = guessed or "application/octet-stream"
        mime = {"video/quicktime": "video/mp4", "video/x-m4v": "video/mp4"}.get(mime.lower(), mime)
        return FileResponse(
            abs_path,
            media_type=mime,
            content_disposition_type="inline",
            headers={"Cache-Control": "private, no-store"},
        )

    if enc:
        key_b64 = row["enc_key"]
        total = crypto.container_size(row["original_name"] or "download.bin", row["sha256"] or "", row["size"] or 0)
        touch_download(row["id"], ip, request.headers.get("user-agent", "-"), encrypted=True)
        headers = {
            "Content-Length": str(total),
            "Content-Disposition": f'attachment; filename="{token}.dat"',
            "Accept-Ranges": "none",
            "Cache-Control": "private, no-store",
            "X-Content-Type-Options": "nosniff",
        }
        return StreamingResponse(
            crypto.encrypt_stream(str(abs_path), key_b64, row["original_name"] or "download.bin", row["sha256"] or ""),
            media_type="application/octet-stream",
            headers=headers,
        )

    touch_download(row["id"], ip, request.headers.get("user-agent", "-"))
    mime = row["mime_type"] or "application/octet-stream"
    filename = (row["original_name"] or "download.bin").replace(chr(34), "")
    return FileResponse(
        abs_path,
        media_type=mime,
        filename=filename,
        headers={"Cache-Control": "private, no-store"},
    )

@app.post("/api/admin/login")
async def admin_login(request: Request, payload: AdminLoginRequest):
    ip = client_ip(request)
    if not secrets.compare_digest(payload.password, settings.admin_password):
        log_event(ip, "ADMIN_LOGIN", "FAIL", detail="BAD_PASSWORD", user_agent=request.headers.get("user-agent","-"), level=logging.WARNING)
        raise HTTPException(401, "invalid password")
    token = secrets.token_urlsafe(32)
    now = utcnow(); exp = now + timedelta(hours=settings.admin_session_hours)
    with connect() as conn:
        conn.execute("INSERT INTO admin_sessions(token,created_at,expires_at) VALUES(?,?,?)", (token, iso(now), iso(exp)))
    log_event(ip, "ADMIN_LOGIN", "SUCCESS", detail="", user_agent=request.headers.get("user-agent","-"))
    resp = JSONResponse({"ok": True})
    resp.set_cookie("shareweb_admin", token, httponly=True, secure=True, samesite="strict", max_age=settings.admin_session_hours*3600, path="/")
    return resp

@app.post("/api/admin/logout")
async def admin_logout(request: Request, shareweb_admin: str | None = Cookie(default=None)):
    if shareweb_admin:
        with connect() as conn:
            conn.execute("DELETE FROM admin_sessions WHERE token=?", (shareweb_admin,))
    resp = JSONResponse({"ok": True})
    resp.delete_cookie("shareweb_admin", path="/")
    return resp

def require_admin(shareweb_admin: str | None = Cookie(default=None)):
    if not require_admin_session(shareweb_admin):
        raise HTTPException(401, "admin authentication required")

# 除登录/登出外的 /api/admin/* 接口都挂在这里, 统一校验管理员会话
admin_api = APIRouter(prefix="/api/admin", dependencies=[Depends(require_admin)])

def _local_tz(tz: int) -> timezone:
    """tz 为浏览器的 Date.getTimezoneOffset() (分钟, UTC 减本地时间; 东八区为 -480)。"""
    return timezone(timedelta(minutes=-max(-840, min(840, tz))))

def _local_day_start(tz: int, days_ago: int = 0) -> datetime:
    zone = _local_tz(tz)
    day = utcnow().astimezone(zone).date() - timedelta(days=days_ago)
    return datetime.combine(day, time.min, tzinfo=zone)

@admin_api.get("/stats")
async def admin_stats(tz: int = 0):
    now = iso(utcnow())
    today = iso(_local_day_start(tz))  # 「今日」按管理员浏览器所在时区计算
    with connect() as conn:
        shares = conn.execute("SELECT COUNT(*) c FROM shares WHERE active=1 AND (expires_at>? OR locked=1)", (now,)).fetchone()["c"]
        file_count_row = conn.execute("SELECT COUNT(*) c, COALESCE(SUM(size),0) b FROM shares WHERE type='file' AND active=1 AND (expires_at>? OR locked=1)", (now,)).fetchone()
        uploads = conn.execute("SELECT COUNT(*) c FROM access_logs WHERE action IN ('UPLOAD','UPLOAD_TEXT') AND created_at>=?", (today,)).fetchone()["c"]
        downloads = conn.execute("SELECT COUNT(*) c FROM access_logs WHERE action='DOWNLOAD' AND created_at>=?", (today,)).fetchone()["c"]
        blacklist = conn.execute("SELECT COUNT(*) c FROM blacklist WHERE active=1").fetchone()["c"]
    return {"active_shares": shares, "file_count": file_count_row["c"], "file_bytes": file_count_row["b"], "today_uploads": uploads, "today_downloads": downloads, "blacklist": blacklist}

_ARCHIVE_EXT = {"zip", "rar", "7z", "tar", "gz", "tgz", "bz2", "xz", "zst", "iso", "dmg"}
_DOC_EXT = {"pdf", "doc", "docx", "xls", "xlsx", "ppt", "pptx", "csv", "txt", "md", "rtf", "odt", "ods", "odp", "epub", "pages", "numbers", "key"}
_APP_EXT = {"exe", "msi", "apk", "ipa", "deb", "rpm", "appimage", "pkg", "bat", "sh", "jar"}

def _file_category(share_type: str, mime: str | None, name: str | None) -> str:
    if share_type == "text":
        return "text"
    mime = (mime or "").lower()
    ext = (name or "").rsplit(".", 1)[-1].lower() if "." in (name or "") else ""
    for prefix in ("video", "image", "audio"):
        if mime.startswith(prefix + "/"):
            return prefix
    if ext in _ARCHIVE_EXT or any(k in mime for k in ("zip", "compressed", "x-tar", "x-7z", "rar")):
        return "archive"
    if ext in _APP_EXT or any(k in mime for k in ("msdownload", "android.package", "x-executable")):
        return "app"
    if ext in _DOC_EXT or mime.startswith("text/") or any(k in mime for k in ("pdf", "officedocument", "msword", "ms-excel", "ms-powerpoint", "opendocument")):
        return "document"
    return "other"

def _overview(days: int, tz: int):
    now = utcnow()
    start = _local_day_start(tz, days - 1)
    offset = f"{-max(-840, min(840, tz)):+d} minutes"
    with connect() as conn:
        trend_rows = conn.execute(
            "SELECT date(created_at, ?) d, SUM(action IN ('UPLOAD','UPLOAD_TEXT')) up, SUM(action='DOWNLOAD') down "
            "FROM access_logs WHERE action IN ('UPLOAD','UPLOAD_TEXT','DOWNLOAD') AND created_at>=? GROUP BY d",
            (offset, iso(start))).fetchall()
        shares = conn.execute("SELECT type, mime_type, original_name, size FROM shares WHERE active=1 AND (expires_at>? OR locked=1)",
                              (iso(now),)).fetchall()
        vis = conn.execute("SELECT ip, hits FROM visitors").fetchall()
    by_day = {r["d"]: r for r in trend_rows}
    trend = []
    for i in range(days):
        d = (start.date() + timedelta(days=i)).isoformat()
        r = by_day.get(d)
        trend.append({"date": d, "uploads": (r["up"] or 0) if r else 0, "downloads": (r["down"] or 0) if r else 0})

    types: dict[str, dict] = {}
    share_bytes = 0
    for r in shares:
        cat = _file_category(r["type"], r["mime_type"], r["original_name"])
        t = types.setdefault(cat, {"category": cat, "count": 0, "bytes": 0})
        t["count"] += 1
        t["bytes"] += r["size"] or 0
        share_bytes += r["size"] or 0

    countries: dict[str, dict] = {}
    for r in vis:
        if visitors.is_loopback(r["ip"]):
            continue
        g = geoip.lookup(r["ip"])
        code = g.get("country_code") or ""
        c = countries.setdefault(code, {"code": code, "en": g.get("country_en"), "zh": g.get("country_zh"), "ips": 0, "hits": 0})
        c["ips"] += 1
        c["hits"] += r["hits"] or 0

    total, used, free = app_settings.disk_usage()
    return {
        "days": days,
        "trend": trend,
        "types": sorted(types.values(), key=lambda x: -x["bytes"]),
        "countries": sorted(countries.values(), key=lambda x: (-x["ips"], -x["hits"])),
        "disk": {"total": total, "used": used, "free": free, "shares": share_bytes},
    }

@admin_api.get("/overview")
async def admin_overview(days: int = 14, tz: int = 0):
    """总览页图表数据: 每日上传/下载、按类型的存储占用、磁盘、访客来源国家。"""
    if days not in (7, 14, 30):
        raise HTTPException(400, "days must be 7, 14 or 30")
    return await run_in_threadpool(_overview, days, tz)

def _settings_payload():
    total, used, free = app_settings.disk_usage()
    evictable = evictable_files()
    return {
        "max_upload_mb": settings.max_upload_mb,
        "auto_evict": settings.auto_evict,
        "evictable_count": len(evictable),
        "evictable_bytes": sum(int(r["size"] or 0) for r in evictable),
        "default_max_upload_mb": app_settings.default_max_upload_mb(),
        "max_upload_mb_cap": app_settings.MAX_UPLOAD_MB_CAP,
        "capacity_bytes": app_settings.upload_capacity_bytes(),
        "disk_reserve_bytes": app_settings.DISK_RESERVE_BYTES,
        "disk": {"total": total, "used": used, "free": free},
    }

@admin_api.get("/settings")
async def admin_get_settings():
    return await run_in_threadpool(_settings_payload)

@admin_api.put("/settings")
async def admin_put_settings(request: Request, payload: AdminSettingsRequest):
    changes = []
    if payload.max_upload_mb is not None and payload.max_upload_mb != settings.max_upload_mb:
        changes.append(f"MAX_UPLOAD_MB={settings.max_upload_mb}->{payload.max_upload_mb}")
        await run_in_threadpool(app_settings.set_max_upload_mb, payload.max_upload_mb)
    if payload.auto_evict is not None and payload.auto_evict != settings.auto_evict:
        changes.append(f"AUTO_EVICT={int(settings.auto_evict)}->{int(payload.auto_evict)}")
        await run_in_threadpool(app_settings.set_auto_evict, payload.auto_evict)
    if changes:
        log_event(client_ip(request), "ADMIN_SETTINGS", "SUCCESS", detail=" ".join(changes))
    return {"ok": True, **(await run_in_threadpool(_settings_payload))}

@admin_api.post("/cleanup")
async def admin_cleanup(request: Request, payload: AdminCleanupRequest):
    if payload.days not in (None, 7, 14):
        raise HTTPException(400, "days must be 7, 14 or null")
    # 删除 GitHub 镜像要走网络, 放进线程池以免卡住整个事件循环。
    removed, removed_bytes = await run_in_threadpool(cleanup_old_files, payload.days)
    label = "ALL" if payload.days is None else f"{payload.days}D"
    log_event(client_ip(request), "ADMIN_CLEANUP", "SUCCESS", detail=f"RANGE={label} REMOVED={removed} BYTES={removed_bytes}")
    return {"ok": True, "removed": removed, "removed_bytes": removed_bytes, "range": label}

@admin_api.get("/files")
async def admin_files():
    return {"items": await run_in_threadpool(list_files)}

@admin_api.post("/files/delete")
async def admin_delete_files(request: Request, payload: AdminDeleteFilesRequest):
    removed, removed_bytes, skipped = await run_in_threadpool(delete_files, payload.ids)
    log_event(client_ip(request), "ADMIN_DELETE_FILES", "SUCCESS", detail=f"REQUESTED={len(payload.ids)} REMOVED={removed} BYTES={removed_bytes} SKIPPED_LOCKED={skipped}")
    return {"ok": True, "removed": removed, "removed_bytes": removed_bytes, "skipped_locked": skipped}

@admin_api.post("/files/lock")
async def admin_lock_files(request: Request, payload: AdminLockFilesRequest):
    changed = await run_in_threadpool(set_files_locked, payload.ids, payload.locked)
    log_event(client_ip(request), "ADMIN_LOCK_FILES" if payload.locked else "ADMIN_UNLOCK_FILES", "SUCCESS", detail=f"IDS={','.join(map(str, payload.ids[:50]))} CHANGED={changed}")
    return {"ok": True, "changed": changed}

def _visitor_list(current_ip: str):
    """访客 + 黑名单合并列表 (最近访问的 2000 个 IP, 加上所有仍生效的黑名单 IP), 带地理信息。"""
    now = iso(utcnow())
    with connect() as conn:
        vis = conn.execute("SELECT * FROM visitors ORDER BY last_seen DESC LIMIT 2000").fetchall()
        bl = conn.execute("SELECT ip, reason, created_at, expires_at FROM blacklist WHERE active=1 AND (expires_at IS NULL OR expires_at>?)", (now,)).fetchall()
    blocked = {r["ip"]: r for r in bl}
    items = {}
    for r in vis:
        if visitors.is_loopback(r["ip"]):
            continue
        items[r["ip"]] = {"ip": r["ip"], "first_seen": r["first_seen"], "last_seen": r["last_seen"], "hits": r["hits"],
                          "last_path": r["last_path"], "user_agent": r["user_agent"]}
    for ip in blocked:
        items.setdefault(ip, {"ip": ip, "first_seen": None, "last_seen": None, "hits": 0, "last_path": None, "user_agent": None})
    out = []
    for ip, it in items.items():
        b = blocked.get(ip)
        it.update({"blocked": bool(b), "block_reason": b["reason"] if b else None, "blocked_at": b["created_at"] if b else None,
                   "block_expires": b["expires_at"] if b else None, "is_me": ip == current_ip, "geo": geoip.lookup(ip)})
        out.append(it)
    return out


def _valid_ips(ips):
    out = []
    for ip in ips:
        try:
            out.append(str(ipaddress.ip_address(ip.strip())))
        except ValueError:
            raise HTTPException(400, f"invalid ip: {ip}")
    return out


@admin_api.get("/visitors")
async def admin_visitors(request: Request):
    await run_in_threadpool(visitors.flush)  # 让刚刚的访问也出现在列表里
    me = client_ip(request)
    return {"items": await run_in_threadpool(_visitor_list, me), "me": me}

@admin_api.post("/visitors/block")
async def admin_block_ips(request: Request, payload: AdminIpsRequest):
    me = client_ip(request)
    ips = _valid_ips(payload.ips)
    # 不允许封禁管理员自己当前的 IP, 以免把自己挡在网站外面
    targets = [ip for ip in ips if ip != me]
    reason = (payload.reason or "").strip() or "blocked from visitor list"
    now = iso(utcnow())
    with connect() as conn:
        for ip in targets:
            conn.execute("INSERT INTO blacklist(ip,reason,created_at,expires_at,active) VALUES(?,?,?,NULL,1) "
                         "ON CONFLICT(ip) DO UPDATE SET reason=excluded.reason, created_at=excluded.created_at, expires_at=NULL, active=1",
                         (ip, reason, now))
    log_event(me, "ADMIN_BLOCK_IPS", "SUCCESS", detail=f"IPS={','.join(targets[:50])} SKIPPED_SELF={len(ips)-len(targets)}")
    return {"ok": True, "blocked": len(targets), "skipped_self": len(ips) - len(targets)}

@admin_api.post("/visitors/allow")
async def admin_allow_ips(request: Request, payload: AdminIpsRequest):
    ips = _valid_ips(payload.ips)
    with connect() as conn:
        changed = 0
        for ip in ips:
            changed += conn.execute("UPDATE blacklist SET active=0 WHERE ip=? AND active=1", (ip,)).rowcount
            conn.execute("DELETE FROM rate_limits WHERE ip=?", (ip,))
    log_event(client_ip(request), "ADMIN_ALLOW_IPS", "SUCCESS", detail=f"IPS={','.join(ips[:50])} CHANGED={changed}")
    return {"ok": True, "allowed": changed}

@app.get("/special", response_class=HTMLResponse)
async def special_page(request: Request):
    return (settings.web_dir / "special.html").read_text(encoding="utf-8")

@app.get("/healthz")
async def healthz():
    return {"ok": True}

app.include_router(admin_api)
