from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_prefix="SHAREWEB_", extra="ignore")

    base_dir: Path = Path("/opt/shareweb")
    # 监听地址/端口在 systemd 的 uvicorn 命令行里设置, 这里只管对外链接
    public_scheme: str = "https"
    public_host: str = "localhost"
    public_port: int = 443
    # 单文件上限的默认值; 管理后台「高级设置」里改过后以数据库里的值为准 (见 app_settings.py)。0 = 不限制
    max_upload_mb: int = 1024
    # 磁盘空间不够放下新上传的文件时, 自动删除最旧的 (未锁定) 文件腾出空间。同样可在「高级设置」里修改
    auto_evict: bool = False
    max_text_mb: int = 10
    retention_days: int = 30
    fail_cooldown_threshold: int = 3
    fail_cooldown_seconds: int = 60
    fail_blacklist_threshold: int = 5
    admin_password: str = "CHANGE_ME"
    admin_session_hours: int = 12
    log_level: str = "INFO"
    trust_proxy_headers: bool = True
    # GitHub 私有仓库镜像 (用于绕过域名白名单)。留空则禁用该功能。
    github_token: str = ""
    github_repo: str = ""          # 形如 "owner/repo"
    github_branch: str = "main"
    # 不超过该大小用 Contents API 镜像 (保留中文文件名); 更大的文件改用草稿 Release 附件
    # (Contents API 对 ~50MB 文件已返回 422)。
    github_max_mb: int = 40
    # 访客 IP 记录保留天数 (仍在黑名单中的不删)
    visitor_retention_days: int = 90

    @property
    def data_dir(self) -> Path:
        return self.base_dir / "data"
    @property
    def log_dir(self) -> Path:
        return self.base_dir / "logs"
    @property
    def db_path(self) -> Path:
        return self.base_dir / "database" / "share.db"
    @property
    def database_dir(self) -> Path:
        return self.base_dir / "database"
    @property
    def geoip_dir(self) -> Path:
        return self.base_dir / "geoip"
    @property
    def web_dir(self) -> Path:
        return self.base_dir / "web"
    @property
    def max_upload_bytes(self) -> int | None:
        """None 表示不限制 (仍受磁盘剩余空间约束)。"""
        return self.max_upload_mb * 1024 * 1024 if self.max_upload_mb > 0 else None
    @property
    def github_max_bytes(self) -> int:
        return self.github_max_mb * 1024 * 1024
    @property
    def max_text_bytes(self) -> int:
        return self.max_text_mb * 1024 * 1024
    @property
    def public_base_url(self) -> str:
        port = f":{self.public_port}" if self.public_port not in (80, 443) else ""
        return f"{self.public_scheme}://{self.public_host}{port}"

settings = Settings()
