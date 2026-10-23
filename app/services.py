import logging
import threading
from datetime import timedelta
from .config import settings
from .database import connect
from .security import utcnow, iso, random_token, random_code, is_blacklisted, check_cooldown, clear_failed_attempts, record_failed_attempt
from .storage import safe_delete
from .crypto import new_key_b64
from . import github_mirror

logger = logging.getLogger(__name__)

# 「文件」分享 (另一种是文本分享)
_FILE_WHERE = "type='file'"
# 仍然有效的分享: 未过期, 或已被管理员锁定。参数: 当前时间
_ALIVE_WHERE = "active=1 AND (expires_at IS NULL OR expires_at>? OR locked=1)"
# 删除分享时需要的列
_PURGE_COLS = "id, storage_path, size, github_path, github_sha"


def log_event(ip, action, result, share_id='-', detail='', user_agent='-', level=logging.INFO):
    try:
        logger.log(level, detail or action, extra={"ip": ip, "action": action, "share_id": share_id})
    except Exception:
        pass
    try:
        with connect() as conn:
            conn.execute(
                "INSERT INTO access_logs(share_id,ip,action,result,user_agent,detail,created_at) VALUES(?,?,?,?,?,?,?)",
                (None if share_id == '-' else share_id, ip, action, result, user_agent, detail, iso(utcnow()))
            )
    except Exception as e:
        logger.warning(f"Failed to log access event to database: {e}")

def generate_unique_code(conn):
    for _ in range(100):
        code = random_code()
        if code == SPECIAL_CODE:
            continue
        if not conn.execute(f"SELECT 1 FROM shares WHERE code=? AND {_ALIVE_WHERE} LIMIT 1", (code, iso(utcnow()))).fetchone():
            return code
    raise RuntimeError("could not allocate a unique 4-digit share code")

def _create_share(kind, original_name, mime_type, size, sha256, storage_name, storage_path):
    now = utcnow(); exp = now + timedelta(days=settings.retention_days)
    token = random_token()
    with connect() as conn:
        code = generate_unique_code(conn)
        cur = conn.execute(
            "INSERT INTO shares(token,code,type,original_name,storage_name,storage_path,size,mime_type,sha256,enc_key,created_at,expires_at) "
            "VALUES(?,?,?,?,?,?,?,?,?,?,?,?)",
            (token, code, kind, original_name, storage_name, storage_path, size, mime_type, sha256, new_key_b64(), iso(now), iso(exp)))
    return cur.lastrowid, token, code, iso(exp)

def create_share_file(original_name, mime_type, size, sha256, storage_name, storage_path, ip, user_agent):
    share_id, token, code, exp = _create_share("file", original_name, mime_type, size, sha256, storage_name, storage_path)
    log_event(ip, "UPLOAD", "SUCCESS", share_id, f"FILE={original_name} SIZE={size} SHA256={sha256} CODE={code}", user_agent)
    return share_id, token, code, exp

def create_share_text(storage_name, storage_path, size, sha256, ip, user_agent):
    share_id, token, code, exp = _create_share("text", "text.txt", "text/plain; charset=utf-8", size, sha256, storage_name, storage_path)
    log_event(ip, "UPLOAD_TEXT", "SUCCESS", share_id, f"SIZE={size} SHA256={sha256} CODE={code}", user_agent)
    return share_id, token, code, exp

def share_status(tokens):
    """首页「本地历史」用: 只读地查询一批分享是否还在。

    返回 {token: "ok" | "expired" | "deleted"}。不像 get_share_by_token 那样顺带停用/删除过期文件。
    """
    tokens = [t for t in dict.fromkeys(tokens) if t]
    if not tokens:
        return {}
    now = iso(utcnow())
    marks = ",".join("?" * len(tokens))
    with connect() as conn:
        rows = conn.execute(f"SELECT token, active, expires_at, locked FROM shares WHERE token IN ({marks})", tokens).fetchall()
    found = {}
    for r in rows:
        alive = r["active"] and (r["locked"] or not r["expires_at"] or r["expires_at"] > now)
        found[r["token"]] = "ok" if alive else "expired"
    return {t: found.get(t, "deleted") for t in tokens}


def get_active_file_by_sha256(sha256):
    with connect() as conn:
        return conn.execute(
            f"SELECT * FROM shares WHERE {_FILE_WHERE} AND sha256=? AND {_ALIVE_WHERE} ORDER BY created_at DESC LIMIT 1",
            (sha256.lower(), iso(utcnow())),
        ).fetchone()


def _remove_stored(row):
    """删除分享的本地文件和 GitHub 镜像 (row 需含 storage_path/github_path/github_sha)。"""
    safe_delete(row["storage_path"])
    _github_cleanup(row)


def _purge(conn, row) -> bool:
    """删除一个未锁定的分享。

    先删数据库记录并再次确认未锁定, 成功后才删文件: 列表查出来之后、真正删除之前
    (GitHub 删除要走网络, 可能耗时几秒) 管理员刚锁定的文件不会被删。返回是否删除。
    """
    if conn.execute("DELETE FROM shares WHERE id=? AND locked=0", (row["id"],)).rowcount != 1:
        return False
    conn.commit()  # 逐个提交, 中途出错时已删的文件与数据库记录保持一致
    _remove_stored(row)
    return True


def _purge_rows(conn, rows):
    """依次删除 rows 中未锁定的分享, 返回 (删除数, 释放字节数)。"""
    removed = removed_bytes = 0
    for row in rows:
        if _purge(conn, row):
            removed += 1
            removed_bytes += int(row["size"] or 0)
    return removed, removed_bytes


def cleanup_old_files(days: int | None):
    """删除 N 天前上传的文件分享; days 为 None 时删除全部文件分享。锁定的文件保留。返回 (删除数, 释放字节数)。"""
    sql, args = f"SELECT {_PURGE_COLS} FROM shares WHERE {_FILE_WHERE} AND locked=0", ()
    if days is not None:
        sql, args = sql + " AND created_at<=?", (iso(utcnow() - timedelta(days=days)),)
    with connect() as conn:
        return _purge_rows(conn, conn.execute(sql, args).fetchall())


def list_files():
    """管理后台文件列表: 所有已保存的文件分享, 最新的在前。"""
    now = iso(utcnow())
    with connect() as conn:
        rows = conn.execute(
            f"SELECT id, token, code, original_name, size, mime_type, created_at, expires_at, download_count, active, github_path, locked "
            f"FROM shares WHERE {_FILE_WHERE} ORDER BY created_at DESC"
        ).fetchall()
    return [{
        "id": r["id"], "token": r["token"], "code": r["code"], "filename": r["original_name"] or "download.bin",
        "size": int(r["size"] or 0), "mime_type": r["mime_type"], "created_at": r["created_at"], "expires_at": r["expires_at"],
        "download_count": r["download_count"] or 0,
        "locked": bool(r["locked"]),
        "expired": not r["locked"] and ((not r["active"]) or bool(r["expires_at"] and r["expires_at"] <= now)),
        "github": bool(r["github_path"]),
    } for r in rows]


def delete_files(ids):
    """按 id 删除文件分享 (本地文件 + GitHub 镜像 + 数据库记录); 只处理文件分享, 不碰文本分享。

    已锁定的文件跳过。返回 (删除数, 释放字节数, 因锁定跳过数)。
    """
    ids = [int(i) for i in ids]
    if not ids:
        return 0, 0, 0
    marks = ",".join("?" * len(ids))
    with connect() as conn:
        rows = conn.execute(f"SELECT {_PURGE_COLS} FROM shares WHERE {_FILE_WHERE} AND id IN ({marks})", ids).fetchall()
        removed, removed_bytes = _purge_rows(conn, rows)
    return removed, removed_bytes, len(rows) - removed


_evict_lock = threading.Lock()


def evictable_files():
    """磁盘不足时可被自动删除的文件 (未锁定的文件分享, 最旧的在前)。文本分享和锁定的文件不在其中。"""
    with connect() as conn:
        return conn.execute(
            f"SELECT {_PURGE_COLS} FROM shares WHERE {_FILE_WHERE} AND locked=0 ORDER BY created_at ASC, id ASC"
        ).fetchall()


def evict_for_space(need_bytes: int, capacity_fn, ip="system") -> bool:
    """磁盘可用空间 (capacity_fn()) 不足 need_bytes 时, 从最旧的文件开始删, 直到够用。

    先估算: 把所有可删文件删光也不够时一个都不删, 直接返回 False, 免得白白删掉文件上传仍然失败。
    加锁, 避免多个同时进行的上传重复删除。
    """
    with _evict_lock:
        if capacity_fn() >= need_bytes:
            return True
        rows = evictable_files()
        if capacity_fn() + sum(int(r["size"] or 0) for r in rows) < need_bytes:
            log_event(ip, "AUTO_EVICT", "INSUFFICIENT", detail=f"NEED={need_bytes} EVICTABLE={len(rows)}", level=logging.WARNING)
            return False
        removed_bytes, ids = 0, []
        with connect() as conn:
            for row in rows:
                if capacity_fn() >= need_bytes:
                    break
                if _purge(conn, row):
                    removed_bytes += int(row["size"] or 0)
                    ids.append(row["id"])
        ok = capacity_fn() >= need_bytes
        log_event(ip, "AUTO_EVICT", "SUCCESS" if ok else "INSUFFICIENT",
                  detail=f"NEED={need_bytes} REMOVED={len(ids)} BYTES={removed_bytes} IDS={','.join(map(str, ids[:50]))}",
                  level=logging.INFO if ok else logging.WARNING)
        return ok


def set_files_locked(ids, locked: bool):
    """锁定/解锁文件分享。锁定时顺带恢复 active (已过期但尚未清理的文件也能救回来)。返回受影响数。"""
    ids = [int(i) for i in ids]
    if not ids:
        return 0
    marks = ",".join("?" * len(ids))
    with connect() as conn:
        if locked:
            cur = conn.execute(f"UPDATE shares SET locked=1, active=1 WHERE {_FILE_WHERE} AND id IN ({marks})", ids)
        else:
            cur = conn.execute(f"UPDATE shares SET locked=0 WHERE {_FILE_WHERE} AND id IN ({marks})", ids)
        return cur.rowcount


def get_share_by_token(token):
    """按链接 token 取有效分享; 已过期 (且未锁定) 的顺带停用并删除文件, 返回 None。

    记录先保留 (首页本地历史据此显示「已过期」而不是「已删除」), 由 cleanup_expired 稍后删除。
    """
    with connect() as conn:
        row = conn.execute("SELECT * FROM shares WHERE token=? AND active=1", (token,)).fetchone()
        if not row:
            return None
        if row["expires_at"] and row["expires_at"] <= iso(utcnow()) and not row["locked"]:
            conn.execute("UPDATE shares SET active=0 WHERE id=?", (row["id"],))
            try:
                _remove_stored(row)
            except Exception:
                logger.exception("failed to remove expired share %s", row["id"])
            return None
        return row


SPECIAL_CODE = "0000"  # 使用说明页的入口, 不会分配给分享


class RedeemBlocked(Exception):
    """提取被拒: 冷却中 (cooldown_until 为结束时间) 或已被拉黑 (cooldown_until 为 None)。"""

    def __init__(self, cooldown_until=None):
        super().__init__(cooldown_until or "blacklisted")
        self.cooldown_until = cooldown_until


def redeem_code(code, ip, user_agent):
    """按提取码查找分享。返回 (row, fail_count, blacklisted); 提取码错误时 row 为 None。"""
    blocked, until = check_cooldown(ip)
    if blocked:
        log_event(ip, "REDEEM", "COOLDOWN", detail=f"UNTIL={until}", user_agent=user_agent, level=logging.WARNING)
        raise RedeemBlocked(until)
    if is_blacklisted(ip):
        log_event(ip, "REDEEM", "BLACKLISTED", user_agent=user_agent, level=logging.WARNING)
        raise RedeemBlocked()
    with connect() as conn:
        row = conn.execute(f"SELECT * FROM shares WHERE code=? AND {_ALIVE_WHERE}", (code, iso(utcnow()))).fetchone()
    if not row:
        count, cooldown, blacklisted = record_failed_attempt(ip)
        detail = f"FAIL_COUNT={count}"
        if cooldown: detail += f" COOLDOWN_UNTIL={cooldown}"
        if blacklisted: detail += " BLACKLIST=TRUE"
        log_event(ip, "REDEEM", "FAIL", detail=detail, user_agent=user_agent, level=logging.WARNING)
        return None, count, blacklisted
    clear_failed_attempts(ip)
    log_event(ip, "REDEEM", "SUCCESS", row["id"], f"CODE={code}", user_agent)
    return row, 0, False


_mirror_locks: dict = {}
_mirror_locks_guard = threading.Lock()


def _mirror_lock(share_id) -> threading.Lock:
    with _mirror_locks_guard:
        return _mirror_locks.setdefault(share_id, threading.Lock())


def mirror_to_github(share_id) -> bool:
    """把文件上传到 GitHub 私仓并记录路径/sha。作为后台任务调用；返回是否成功。

    同一分享加锁: 上传后的后台镜像还没完成时用户点了「通过 GitHub 下载」, 会等它完成而不是再传一份。
    """
    if not github_mirror.enabled():
        return False
    with _mirror_lock(share_id):
        with connect() as conn:
            row = conn.execute("SELECT id, type, token, original_name, storage_path, github_path FROM shares WHERE id=?", (share_id,)).fetchone()
        if not row or row["type"] != "file":
            return False
        if row["github_path"]:
            return True
        abs_path = settings.data_dir / row["storage_path"]
        if not abs_path.is_file():
            return False
        try:
            result = github_mirror.mirror(row["token"], row["original_name"] or "download.bin", str(abs_path))
        except Exception:
            logger.exception("github mirror upload error")
            return False
        if not result:
            return False
        remote, sha = result
        with connect() as conn:
            updated = conn.execute("UPDATE shares SET github_path=?, github_sha=? WHERE id=?", (remote, sha, share_id)).rowcount
        if not updated:
            # 上传期间分享已被清理, 删掉刚传上去的副本以免成为孤儿。
            github_mirror.delete(remote, sha)
            return False
        log_event("system", "GITHUB_MIRROR", "SUCCESS", share_id, f"PATH={remote}")
        return True


def get_github_download_url(share_id):
    """返回 {"url": 短时效直链, "filename": 下载后的实际文件名}；若尚未镜像则即时上传一次。"""
    if not github_mirror.enabled():
        return None
    query = "SELECT github_path, github_sha, original_name FROM shares WHERE id=?"
    with connect() as conn:
        row = conn.execute(query, (share_id,)).fetchone()
    if row and not row["github_path"]:
        if not mirror_to_github(share_id):
            return None
        with connect() as conn:
            row = conn.execute(query, (share_id,)).fetchone()
    if not row or not row["github_path"]:
        return None
    try:
        url = github_mirror.temp_download_url(row["github_path"])
    except Exception:
        logger.exception("github temp url error")
        return None
    if not url:
        return None
    return {"url": url, "filename": github_mirror.download_filename(row["github_path"], row["github_sha"], row["original_name"])}


def _github_cleanup(row):
    """尽力从 GitHub 删除已镜像的文件。"""
    gp, gs = row["github_path"], row["github_sha"]
    if github_mirror.enabled() and gp and gs:
        try:
            github_mirror.delete(gp, gs)
        except Exception:
            logger.warning("github cleanup delete failed for %s", gp)


def touch_download(share_id, ip, user_agent, encrypted=False):
    try:
        with connect() as conn:
            conn.execute("UPDATE shares SET download_count=download_count+1 WHERE id=?", (share_id,))
    except Exception as e:
        logger.warning(f"Failed to update download count: {e}")
    log_event(ip, "DOWNLOAD", "SUCCESS", share_id, "MODE=ENC" if encrypted else "", user_agent)

def cleanup_expired():
    """删除已过期且未锁定的分享, 以及过期的管理员会话和临时黑名单。返回删除的分享数。"""
    now = iso(utcnow())
    with connect() as conn:
        rows = conn.execute(f"SELECT {_PURGE_COLS} FROM shares WHERE expires_at IS NOT NULL AND expires_at<=? AND locked=0", (now,)).fetchall()
        removed, _ = _purge_rows(conn, rows)
        conn.execute("DELETE FROM admin_sessions WHERE expires_at<=?", (now,))
        conn.execute("DELETE FROM blacklist WHERE active=1 AND expires_at IS NOT NULL AND expires_at<=?", (now,))
    if removed:
        log_event("system", "CLEANUP", "SUCCESS", detail=f"REMOVED={removed}")
    return removed
