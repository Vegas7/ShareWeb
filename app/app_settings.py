"""管理后台可修改的运行时设置。

存在数据库 app_settings 表里, 启动时读入并覆盖 settings 上对应的字段 (.env 中的值只作默认值)。
只有一个 uvicorn 进程, 改动后直接更新内存中的 settings 即可立即生效。
"""
import shutil

from .config import settings
from .database import connect
from .security import utcnow, iso

# 无论上限设多少, 都给磁盘留出这么多空间, 以免上传把磁盘写满拖垮数据库和日志。
DISK_RESERVE_BYTES = 1024 ** 3
# 自定义上限允许的最大值 (1 TB); 再大也没有意义, 实际受磁盘剩余空间约束。
MAX_UPLOAD_MB_CAP = 1024 * 1024

_DEFAULT_MAX_UPLOAD_MB = settings.max_upload_mb


def load():
    with connect() as conn:
        rows = {r["key"]: r["value"] for r in conn.execute("SELECT key, value FROM app_settings")}
    if "max_upload_mb" in rows:
        try:
            settings.max_upload_mb = max(0, int(rows["max_upload_mb"]))
        except ValueError:
            pass
    if "auto_evict" in rows:
        settings.auto_evict = rows["auto_evict"] == "1"


def _save(key: str, value: str):
    with connect() as conn:
        conn.execute("INSERT INTO app_settings(key,value,updated_at) VALUES(?,?,?) "
                     "ON CONFLICT(key) DO UPDATE SET value=excluded.value, updated_at=excluded.updated_at",
                     (key, value, iso(utcnow())))


def set_max_upload_mb(mb: int):
    _save("max_upload_mb", str(mb))
    settings.max_upload_mb = mb


def set_auto_evict(on: bool):
    _save("auto_evict", "1" if on else "0")
    settings.auto_evict = on


def default_max_upload_mb() -> int:
    return _DEFAULT_MAX_UPLOAD_MB


def disk_usage():
    """data 目录所在磁盘的 (total, used, free) 字节数。"""
    u = shutil.disk_usage(settings.data_dir)
    return u.total, u.used, u.free


def upload_capacity_bytes() -> int:
    """当前磁盘还能接收的最大单个文件 (剩余空间减去保留空间)。"""
    return max(0, disk_usage()[2] - DISK_RESERVE_BYTES)
