from fastapi import Request, HTTPException
from .config import settings
from .security import is_blacklisted

def client_ip(request: Request) -> str:
    if settings.trust_proxy_headers:
        xff = request.headers.get("x-forwarded-for")
        if xff:
            return xff.split(",")[0].strip()
        xri = request.headers.get("x-real-ip")
        if xri:
            return xri.strip()
    return request.client.host if request.client else "unknown"

def ensure_not_blacklisted(request: Request):
    ip = client_ip(request)
    if is_blacklisted(ip):
        raise HTTPException(status_code=403, detail="IP blacklisted")
    return ip
