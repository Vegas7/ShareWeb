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
    locked INTEGER NOT NULL DEFAULT 0,
    api_key_id INTEGER
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
-- 管理员密码输错的次数 (登录和修改密码共用), 见 security.record_admin_failure
CREATE TABLE IF NOT EXISTS admin_login_fails (
    ip TEXT PRIMARY KEY,
    fail_count INTEGER NOT NULL DEFAULT 0,
    locked_until TEXT,
    last_fail_at TEXT NOT NULL
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
-- 断点续传中尚未完成的上传 (见 resumable.py); 已收到的数据在 data/<前两位>/.part-<id>
CREATE TABLE IF NOT EXISTS uploads (
    id TEXT PRIMARY KEY,
    sha256 TEXT NOT NULL,
    size INTEGER NOT NULL,
    filename TEXT,
    content_type TEXT,
    ip TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    api_key_id INTEGER
);
-- 外部 API 的密钥 (见 apikeys.py)。只存 SHA-256, 明文只在创建时显示一次
CREATE TABLE IF NOT EXISTS api_keys (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    prefix TEXT NOT NULL,
    key_hash TEXT NOT NULL UNIQUE,
    created_at TEXT NOT NULL,
    last_used_at TEXT,
    last_ip TEXT,
    use_count INTEGER NOT NULL DEFAULT 0
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
        # 通过外部 API 创建时记下是哪个密钥 (网页上传为 NULL); 该密钥可列出 / 删除自己创建的分享
        "api_key_id": "INTEGER",
    },
    "uploads": {
        "api_key_id": "INTEGER",
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
        conn.execute("CREATE INDEX IF NOT EXISTS idx_shares_api_key ON shares(api_key_id)")
