"""访客 IP 的国家 / ASN / 运营商识别 —— 使用本地离线库 DB-IP Lite (CC BY 4.0, https://db-ip.com)。

数据库由 shareweb-geoip.timer 每月更新到 <base_dir>/geoip/; 这里发现文件被替换后自动重新打开。
查询完全在本机进行, 访客 IP 不会发给任何第三方。数据库不存在时所有查询返回空结果。
"""
from __future__ import annotations

import ipaddress
import logging
import threading
import time

from .config import settings

logger = logging.getLogger(__name__)

_FILES = {"country": "dbip-country-lite.mmdb", "asn": "dbip-asn-lite.mmdb"}
_CHECK_INTERVAL = 60  # 秒; 多久检查一次文件是否被更新

_lock = threading.Lock()
_readers: dict = {}
_mtimes: dict = {}
_last_check = 0.0
_cache: dict = {}


def _refresh():
    global _last_check
    now = time.monotonic()
    if now - _last_check < _CHECK_INTERVAL and _readers:
        return
    _last_check = now
    try:
        import maxminddb
    except ImportError:
        return
    for kind, name in _FILES.items():
        path = settings.geoip_dir / name
        try:
            mtime = path.stat().st_mtime
        except OSError:
            _readers.pop(kind, None)
            continue
        if _mtimes.get(kind) != mtime:
            try:
                _readers[kind] = maxminddb.open_database(str(path))
                _mtimes[kind] = mtime
                _cache.clear()
            except Exception:
                logger.exception("failed to open geoip database %s", path)


def lookup(ip: str) -> dict:
    """返回 {"country_code", "country_en", "country_zh", "asn", "as_org"} (查不到的字段为 None); 内网/无效地址返回 {}。"""
    try:
        addr = ipaddress.ip_address(ip)
    except ValueError:
        return {}
    if not addr.is_global:
        return {}
    with _lock:
        _refresh()
        if ip in _cache:
            return _cache[ip]
        country = asn = None
        try:
            if "country" in _readers:
                country = _readers["country"].get(ip)
            if "asn" in _readers:
                asn = _readers["asn"].get(ip)
        except Exception:
            logger.exception("geoip lookup failed for %s", ip)
        c = (country or {}).get("country") or {}
        names = c.get("names") or {}
        result = {
            "country_code": c.get("iso_code"),
            "country_en": names.get("en"),
            "country_zh": names.get("zh-CN") or names.get("en"),
            "asn": (asn or {}).get("autonomous_system_number"),
            "as_org": (asn or {}).get("autonomous_system_organization"),
        }
        if len(_cache) > 50000:
            _cache.clear()
        _cache[ip] = result
        return result
