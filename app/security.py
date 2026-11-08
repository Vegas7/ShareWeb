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

# ---- 管理员密码输错限制 (按 IP) ----
# 每输错 ADMIN_FAIL_LIMIT 次锁定一段时间, 第一次 15 分钟, 之后每次翻倍, 最长 24 小时;
# 24 小时内没有再输错则从头计数, 输对即清零。只锁这个 IP 的登录 / 改密码, 不拉黑整站访问。
ADMIN_FAIL_LIMIT = 5
_ADMIN_LOCK_FIRST = timedelta(minutes=15)
_ADMIN_LOCK_MAX = timedelta(hours=24)
_ADMIN_FAIL_RESET = timedelta(hours=24)

def admin_locked_until(ip: str) -> str | None:
    """该 IP 被锁定时返回解锁时间 (ISO), 否则 None。"""
    with connect() as conn:
        row = conn.execute("SELECT locked_until FROM admin_login_fails WHERE ip=?", (ip,)).fetchone()
    until = row["locked_until"] if row else None
    return until if until and until > iso(utcnow()) else None

def record_admin_failure(ip: str) -> tuple[int, str | None]:
    """记一次输错, 返回 (锁定前还能再试几次, 锁定到何时 / None)。"""
    now = utcnow()
    with connect() as conn:
        row = conn.execute("SELECT fail_count, last_fail_at FROM admin_login_fails WHERE ip=?", (ip,)).fetchone()
        count = row["fail_count"] if row and row["last_fail_at"] > iso(now - _ADMIN_FAIL_RESET) else 0
        count += 1
        locked_until = None
        if count % ADMIN_FAIL_LIMIT == 0:
            locks = count // ADMIN_FAIL_LIMIT
            locked_until = iso(now + min(_ADMIN_LOCK_FIRST * 2 ** (locks - 1), _ADMIN_LOCK_MAX))
        conn.execute("INSERT INTO admin_login_fails(ip,fail_count,locked_until,last_fail_at) VALUES(?,?,?,?) "
                     "ON CONFLICT(ip) DO UPDATE SET fail_count=excluded.fail_count, locked_until=excluded.locked_until, "
                     "last_fail_at=excluded.last_fail_at", (ip, count, locked_until, iso(now)))
    return ADMIN_FAIL_LIMIT - count % ADMIN_FAIL_LIMIT, locked_until

def clear_admin_failures(ip: str):
    with connect() as conn:
        conn.execute("DELETE FROM admin_login_fails WHERE ip=?", (ip,))

def require_admin_session(token: str | None) -> bool:
    if not token:
        return False
    now = iso(utcnow())
    with connect() as conn:
        row = conn.execute("SELECT 1 FROM admin_sessions WHERE token=? AND expires_at>?", (token, now)).fetchone()
        return row is not None
