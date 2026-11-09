"""外部 API 的密钥。

密钥形如 swk_<43 个随机字符>, 在管理后台的「API」页创建; 数据库只存它的 SHA-256 (密钥本身是高熵随机串,
不需要慢哈希), 明文只在创建时显示一次。请求时放在 Authorization: Bearer <密钥> 或 X-API-Key 头里。
删除密钥后立即失效; 用它创建的分享保留, 照常到期。
"""
import hashlib
import secrets

from .database import connect
from .security import iso, utcnow

KEY_PREFIX = "swk_"
_SHOWN_PREFIX = 12  # 列表里显示密钥开头几位, 方便辨认是哪一把


def _hash(key: str) -> str:
    return hashlib.sha256(key.encode()).hexdigest()


def create_key(name: str) -> dict:
    key = KEY_PREFIX + secrets.token_urlsafe(32)
    now = iso(utcnow())
    with connect() as conn:
        cur = conn.execute("INSERT INTO api_keys(name,prefix,key_hash,created_at) VALUES(?,?,?,?)",
                           (name, key[:_SHOWN_PREFIX], _hash(key), now))
    return {"id": cur.lastrowid, "name": name, "prefix": key[:_SHOWN_PREFIX], "created_at": now, "key": key}


def list_keys() -> list[dict]:
    now = iso(utcnow())
    with connect() as conn:
        rows = conn.execute(
            "SELECT k.id, k.name, k.prefix, k.created_at, k.last_used_at, k.last_ip, k.use_count, "
            "(SELECT COUNT(*) FROM shares s WHERE s.api_key_id=k.id AND s.active=1 "
            " AND (s.expires_at IS NULL OR s.expires_at>? OR s.locked=1)) AS share_count "
            "FROM api_keys k ORDER BY k.id DESC", (now,)).fetchall()
    return [dict(r) for r in rows]


def delete_key(key_id: int) -> bool:
    with connect() as conn:
        return conn.execute("DELETE FROM api_keys WHERE id=?", (key_id,)).rowcount == 1


def authenticate(key: str, ip: str):
    """密钥有效时返回它的记录 (并记下最近使用时间 / IP / 次数), 否则 None。"""
    if not key or not key.startswith(KEY_PREFIX) or len(key) > 200:
        return None
    with connect() as conn:
        row = conn.execute("SELECT id, name FROM api_keys WHERE key_hash=?", (_hash(key),)).fetchone()
        if row:
            conn.execute("UPDATE api_keys SET last_used_at=?, last_ip=?, use_count=use_count+1 WHERE id=?",
                         (iso(utcnow()), ip, row["id"]))
    return row
