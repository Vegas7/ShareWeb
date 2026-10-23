from datetime import datetime, timedelta, timezone
import secrets
from .database import connect
from .config import settings

def utcnow():
    return datetime.now(timezone.utc)

def iso(dt):
    return dt.astimezone(timezone.utc).isoformat()

def random_token():
    return secrets.token_urlsafe(32)  # 43 个字符

def random_code():
    return f"{secrets.randbelow(10000):04d}"

def is_blacklisted(ip: str) -> bool:
    now = iso(utcnow())
    with connect() as conn:
        row = conn.execute("SELECT expires_at FROM blacklist WHERE ip=? AND active=1", (ip,)).fetchone()
        if not row:
            return False
        if row["expires_at"] and row["expires_at"] <= now:
            conn.execute("UPDATE blacklist SET active=0 WHERE ip=?", (ip,))
            return False
        return True

def check_cooldown(ip: str):
    """返回 (是否在冷却中, 冷却结束时间)。"""
    with connect() as conn:
        row = conn.execute("SELECT cooldown_until FROM rate_limits WHERE ip=?", (ip,)).fetchone()
    cooldown = row["cooldown_until"] if row else None
    if cooldown and cooldown > iso(utcnow()):
        return True, cooldown
    return False, None

def record_failed_attempt(ip: str):
    now = utcnow()
    with connect() as conn:
        row = conn.execute("SELECT fail_count FROM rate_limits WHERE ip=?", (ip,)).fetchone()
        count = (row["fail_count"] if row else 0) + 1
        cooldown = None
        if count >= settings.fail_cooldown_threshold:
            cooldown = iso(now + timedelta(seconds=settings.fail_cooldown_seconds))
        conn.execute("INSERT INTO rate_limits(ip,fail_count,cooldown_until,last_fail_at) VALUES(?,?,?,?) ON CONFLICT(ip) DO UPDATE SET fail_count=excluded.fail_count,cooldown_until=excluded.cooldown_until,last_fail_at=excluded.last_fail_at", (ip, count, cooldown, iso(now)))
        if count >= settings.fail_blacklist_threshold:
            conn.execute("INSERT OR IGNORE INTO blacklist(ip,reason,created_at,active) VALUES(?,?,?,1)", (ip, f"{count} failed share-code attempts", iso(now)))
        return count, cooldown, count >= settings.fail_blacklist_threshold

def clear_failed_attempts(ip: str):
    with connect() as conn:
        conn.execute("DELETE FROM rate_limits WHERE ip=?", (ip,))

def require_admin_session(token: str | None) -> bool:
    if not token:
        return False
    now = iso(utcnow())
    with connect() as conn:
        row = conn.execute("SELECT 1 FROM admin_sessions WHERE token=? AND expires_at>?", (token, now)).fetchone()
        return row is not None
