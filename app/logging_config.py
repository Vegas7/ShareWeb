import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
from .config import settings

class ContextFormatter(logging.Formatter):
    def format(self, record):
        if not hasattr(record, "ip"):
            record.ip = "-"
        if not hasattr(record, "action"):
            record.action = "-"
        if not hasattr(record, "share_id"):
            record.share_id = "-"
        return super().format(record)


def setup_logging():
    Path(settings.log_dir).mkdir(parents=True, exist_ok=True)
    root = logging.getLogger()
    if root.handlers:
        return
    root.setLevel(getattr(logging, settings.log_level.upper(), logging.INFO))
    fmt = ContextFormatter("%(asctime)s %(levelname)s IP=%(ip)s ACTION=%(action)s SHARE=%(share_id)s %(message)s")
    app_handler = RotatingFileHandler(settings.log_dir / "app.log", maxBytes=10*1024*1024, backupCount=7, encoding="utf-8")
    app_handler.setFormatter(fmt)
    root.addHandler(app_handler)
    console = logging.StreamHandler()
    console.setFormatter(fmt)
    root.addHandler(console)
