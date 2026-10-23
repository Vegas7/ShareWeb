"""访客 IP 记录: 请求先计入内存, 后台每隔几秒批量写入 visitors 表, 不拖慢请求本身。"""
from __future__ import annotations

import threading

from .database import connect
from .security import utcnow, iso

# 不记录的路径 (静态资源 / 健康检查)
_SKIP_PREFIXES = ("/static/", "/healthz", "/favicon.ico")

_lock = threading.Lock()
_pending: dict = {}


def should_record(path: str) -> bool:
    return not path.startswith(_SKIP_PREFIXES)


def is_loopback(ip: str) -> bool:
    """本机地址 (服务器自己发起的请求, 如本地测试/健康检查) 不算访客。"""
    return ip.startswith("127.") or ip in ("::1", "localhost")


def record(ip: str, path: str, user_agent: str | None):
    if not ip or ip == "unknown" or is_loopback(ip):
        return
    now = iso(utcnow())
    with _lock:
        v = _pending.get(ip)
        if v is None:
            _pending[ip] = {"first": now, "last": now, "hits": 1, "path": path[:200], "ua": (user_agent or "")[:300]}
        else:
            v["last"] = now
            v["hits"] += 1
            v["path"] = path[:200]
            v["ua"] = (user_agent or "")[:300]


def flush() -> int:
    """把内存中的计数写入数据库; 返回写入的 IP 数。"""
    with _lock:
        if not _pending:
            return 0
        batch = list(_pending.items())
        _pending.clear()
    with connect() as conn:
        conn.executemany(
            "INSERT INTO visitors(ip, first_seen, last_seen, hits, last_path, user_agent) VALUES(?,?,?,?,?,?) "
            "ON CONFLICT(ip) DO UPDATE SET last_seen=excluded.last_seen, hits=visitors.hits+excluded.hits, "
            "last_path=excluded.last_path, user_agent=excluded.user_agent",
            [(ip, v["first"], v["last"], v["hits"], v["path"], v["ua"]) for ip, v in batch],
        )
    return len(batch)


def prune(retention_days: int) -> int:
    """删除超过保留期没再出现的访客 (仍在黑名单中的保留)。"""
    from datetime import timedelta
    cutoff = iso(utcnow() - timedelta(days=retention_days))
    with connect() as conn:
        cur = conn.execute(
            "DELETE FROM visitors WHERE last_seen < ? AND ip NOT IN (SELECT ip FROM blacklist WHERE active=1)", (cutoff,)
        )
        return cur.rowcount
