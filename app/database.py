import sqlite3
from .config import settings

def connect():
    conn = sqlite3.connect(settings.db_path, timeout=5, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys=ON")
    return conn

_SCHEMA = """
CREATE TABLE IF NOT EXISTS shares (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    token TEXT NOT NULL UNIQUE,
    code TEXT NOT NULL,
    type TEXT NOT NULL DEFAULT 'file',
    original_name TEXT,
    storage_name TEXT,
    storage_path TEXT,
    size INTEGER NOT NULL DEFAULT 0,
    mime_type TEXT,
    sha256 TEXT,
    created_at TEXT NOT NULL,
    expires_at TEXT NOT NULL,
    download_count INTEGER NOT NULL DEFAULT 0,
    active INTEGER NOT NULL DEFAULT 1,
    -- 每个分享独立的 AES-256 密钥 (base64), 用于加密/混淆下载
    enc_key TEXT,
    github_path TEXT,
    github_sha TEXT,
    -- 管理员锁定: 锁定的文件不过期, 也不会被手动/自动清理删除, 直到解锁
    locked INTEGER NOT NULL DEFAULT 0
);
CREATE TABLE IF NOT EXISTS access_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    share_id INTEGER,
    ip TEXT NOT NULL,
    action TEXT NOT NULL,
    result TEXT NOT NULL,
    user_agent TEXT,
    detail TEXT,
    created_at TEXT NOT NULL,
    FOREIGN KEY(share_id) REFERENCES shares(id) ON DELETE SET NULL
);
CREATE TABLE IF NOT EXISTS visitors (
    ip TEXT PRIMARY KEY,
    first_seen TEXT NOT NULL,
    last_seen TEXT NOT NULL,
    hits INTEGER NOT NULL DEFAULT 0,
    last_path TEXT,
    user_agent TEXT
);
CREATE TABLE IF NOT EXISTS blacklist (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ip TEXT NOT NULL UNIQUE,
    reason TEXT NOT NULL,
    created_at TEXT NOT NULL,
    expires_at TEXT,
    active INTEGER NOT NULL DEFAULT 1
);
CREATE TABLE IF NOT EXISTS rate_limits (
    ip TEXT PRIMARY KEY,
    fail_count INTEGER NOT NULL DEFAULT 0,
    cooldown_until TEXT,
    last_fail_at TEXT
);
CREATE TABLE IF NOT EXISTS admin_sessions (
    token TEXT PRIMARY KEY,
    created_at TEXT NOT NULL,
    expires_at TEXT NOT NULL
);
-- 管理后台可修改的运行时设置 (覆盖 .env 中的默认值)
CREATE TABLE IF NOT EXISTS app_settings (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL,
    updated_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_shares_code_active ON shares(code, active, expires_at);
CREATE INDEX IF NOT EXISTS idx_shares_expires ON shares(expires_at);
CREATE INDEX IF NOT EXISTS idx_visitors_last_seen ON visitors(last_seen);
CREATE INDEX IF NOT EXISTS idx_access_logs_created ON access_logs(created_at);
"""

# 旧版本数据库里还没有的列 (新建的库在上面的 CREATE TABLE 里已包含)
_ADDED_COLUMNS = {
    "shares": {
        "enc_key": "TEXT",
        "github_path": "TEXT",
        "github_sha": "TEXT",
        "locked": "INTEGER NOT NULL DEFAULT 0",
    },
}

def init_db():
    settings.db_path.parent.mkdir(parents=True, exist_ok=True)
    with connect() as conn:
        conn.execute("PRAGMA journal_mode=WAL")
        conn.executescript(_SCHEMA)
        for table, columns in _ADDED_COLUMNS.items():
            existing = {row["name"] for row in conn.execute(f"PRAGMA table_info({table})")}
            for name, ddl in columns.items():
                if name not in existing:
                    conn.execute(f"ALTER TABLE {table} ADD COLUMN {name} {ddl}")
