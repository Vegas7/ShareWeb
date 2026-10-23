"""GitHub 私有仓库镜像 —— 用于绕过「域名白名单」的下载拦截。

设计要点（安全）：
- Personal Access Token 只存在服务器 `.env` (SHAREWEB_GITHUB_TOKEN)，**永不下发给客户端**。
- 上传文件后，客户端点「GitHub 下载」时，服务器用自己的 token 调 GitHub API 拿到一个
  **短时效、仅对该文件、会自动失效**的下载直链再返回给客户端。
  泄露的顶多是一个几分钟后作废的单文件链接，PAT 本身不外泄。

两种存储方式 (按文件大小自动选择)：
- <= SHAREWEB_GITHUB_MAX_MB (默认 40MB)：Contents API 存到 files/<token>/<原文件名>。
  直链在 raw.githubusercontent.com，保留中文文件名。Contents API 要求 base64 整体提交，
  实测 50MB 级文件即返回 422，故只用于小文件。文件会进入 git 历史 (删除后历史仍保留)。
- 更大的文件 (单个 < 2GiB)：每个分享建一个草稿 Release，把原始文件流式上传为附件。
  草稿不会创建 git tag；删除 Release 即彻底删除附件，不留 git 历史。
  直链在 release-assets.githubusercontent.com。GitHub 会去掉附件名里的非 ASCII 字符
  (如 "测试 report v1.txt" 变成 "report.v1.txt")，所以下载链接会带上实际文件名，
  前端据此提示用户改回原名。

数据库字段：Contents 方式 github_path=仓库路径, github_sha=blob sha；
Release 方式 github_path="release:<release_id>:<asset_id>", github_sha=GitHub 实际保存的附件名。

未配置 token/repo 时，本模块所有功能自动禁用（enabled() 返回 False）。
"""
from __future__ import annotations

import base64
import json
import logging
import os
import tempfile
import urllib.request
import urllib.parse
import urllib.error

from .config import settings
from .crypto import clean_filename as _clean_name

logger = logging.getLogger(__name__)

API = "https://api.github.com"
_TIMEOUT = 60
# 大文件上传完成后 GitHub 还要处理一会儿才响应, 单独放宽。
_UPLOAD_TIMEOUT = 600
# GitHub Release 单个附件须小于 2GiB, 留一点余量。
RELEASE_MAX_BYTES = 2000 * 1024 * 1024
_RELEASE_PREFIX = "release:"


def enabled() -> bool:
    return bool(settings.github_token and settings.github_repo)


def fits(size: int) -> bool:
    """文件是否在可镜像的大小范围内。"""
    return int(size) <= RELEASE_MAX_BYTES


def _uses_contents(size: int) -> bool:
    return int(size) <= settings.github_max_bytes


def _headers() -> dict:
    return {
        "Authorization": f"Bearer {settings.github_token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "ShareWeb",
    }


def _quote_path(remote_path: str) -> str:
    # 逐段编码，保留 '/' 分隔符（支持中文文件名）。
    return "/".join(urllib.parse.quote(seg) for seg in remote_path.split("/"))


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    """附件下载接口返回 302 到签名直链; 不跟随, 只取 Location (跟随会把 token 带过去且下载整个文件)。"""

    def redirect_request(self, *args, **kwargs):
        return None


_no_redirect_opener = urllib.request.build_opener(_NoRedirect)


def _request(method: str, url: str, body: dict | None = None, *, stream=None, length: int = 0,
             content_type: str = "application/json", timeout: int = _TIMEOUT) -> tuple[int, dict]:
    headers = _headers()
    if stream is not None:
        data = stream
        headers["Content-Type"] = content_type
        headers["Content-Length"] = str(length)
    else:
        data = json.dumps(body).encode("utf-8") if body is not None else None
    req = urllib.request.Request(url, data=data, method=method, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read()
            return resp.status, (json.loads(raw) if raw else {})
    except urllib.error.HTTPError as e:
        raw = e.read()
        try:
            payload = json.loads(raw) if raw else {}
        except Exception:
            payload = {"message": raw.decode("utf-8", "replace")}
        return e.code, payload


def remote_path_for(token: str, original_name: str) -> str:
    """仓库内路径：files/<token>/<原文件名>，让下载直链的文件名就是原名。"""
    return f"files/{token}/{_clean_name(original_name)}"


def mirror(token: str, original_name: str, local_abs_path: str) -> tuple[str, str] | None:
    """镜像本地文件, 按大小选择 Contents 或 Release。返回 (github_path, github_sha)，失败返回 None。"""
    size = os.path.getsize(local_abs_path)
    if not fits(size):
        logger.info("github mirror skipped, %d bytes exceeds limit %d", size, RELEASE_MAX_BYTES)
        return None
    if _uses_contents(size):
        remote = remote_path_for(token, original_name)
        sha = upload(remote, local_abs_path)
        return (remote, sha) if sha else None
    return _upload_release(token, original_name, local_abs_path, size)


def upload(remote_path: str, local_abs_path: str) -> str | None:
    """把本地文件 PUT 到仓库 (Contents API)，返回 blob 的 content sha；失败返回 None。

    JSON 请求体 (含 base64 内容) 边编码边写入磁盘上的匿名临时文件再流式发送，
    内存占用恒定 (原先整文件 read_bytes + base64 + json.dumps 峰值约为文件大小的 4 倍)。
    """
    url = f"{API}/repos/{settings.github_repo}/contents/{_quote_path(remote_path)}"
    meta = json.dumps({"message": f"shareweb: add {remote_path}", "branch": settings.github_branch})
    # 放在 data 目录而不是 /tmp: 后者可能是 tmpfs (占内存)。
    with tempfile.TemporaryFile(dir=settings.data_dir) as body, open(local_abs_path, "rb") as src:
        body.write(meta[:-1].encode("utf-8") + b', "content": "')
        while True:
            chunk = src.read(3 * 256 * 1024)  # 3 的倍数, 分块 base64 拼接后与整体编码一致
            if not chunk:
                break
            body.write(base64.b64encode(chunk))
        body.write(b'"}')
        length = body.tell()
        body.seek(0)
        status, payload = _request("PUT", url, stream=body, length=length, timeout=_UPLOAD_TIMEOUT)
    if status in (200, 201):
        return (payload.get("content") or {}).get("sha")
    logger.warning("github upload failed %s: %s", status, payload.get("message"))
    return None


def _upload_release(token: str, original_name: str, local_abs_path: str, size: int) -> tuple[str, str] | None:
    """建一个草稿 Release 并把原始文件流式上传为附件 (不经 base64, 内存占用恒定)。"""
    name = _clean_name(original_name)
    status, rel = _request("POST", f"{API}/repos/{settings.github_repo}/releases", {
        "tag_name": f"sw-{token}",   # 草稿不会真正创建这个 tag
        "name": f"shareweb {token}",
        "body": f"ShareWeb mirror of {name}",
        "draft": True,
    })
    if status != 201:
        logger.warning("github release create failed %s: %s", status, rel.get("message"))
        return None
    release_id = rel["id"]
    upload_url = rel["upload_url"].split("{", 1)[0] + "?name=" + urllib.parse.quote(name)
    try:
        with open(local_abs_path, "rb") as src:
            status, asset = _request("POST", upload_url, stream=src, length=size,
                                     content_type="application/octet-stream", timeout=_UPLOAD_TIMEOUT)
    except Exception:
        logger.exception("github release asset upload error")
        status, asset = 0, {}
    if status != 201:
        logger.warning("github release asset upload failed %s: %s", status, asset.get("message") or asset.get("errors"))
        _request("DELETE", f"{API}/repos/{settings.github_repo}/releases/{release_id}")
        return None
    return f"{_RELEASE_PREFIX}{release_id}:{asset['id']}", asset.get("name") or name


def _parse_release(github_path: str) -> tuple[str, str] | None:
    if not github_path or not github_path.startswith(_RELEASE_PREFIX):
        return None
    release_id, _, asset_id = github_path[len(_RELEASE_PREFIX):].partition(":")
    return release_id, asset_id


def download_filename(github_path: str, github_sha: str, original_name: str) -> str:
    """通过 GitHub 下载时浏览器实际保存的文件名。"""
    if _parse_release(github_path):
        return github_sha or _clean_name(original_name)
    return _clean_name(original_name)


def temp_download_url(github_path: str) -> str | None:
    """取该文件的短时效直链（私有仓库的直链含临时签名，几分钟后失效）。"""
    rel = _parse_release(github_path)
    if rel:
        url = f"{API}/repos/{settings.github_repo}/releases/assets/{rel[1]}"
        headers = _headers()
        headers["Accept"] = "application/octet-stream"
        req = urllib.request.Request(url, headers=headers)
        try:
            with _no_redirect_opener.open(req, timeout=_TIMEOUT) as resp:
                # 200 表示 GitHub 直接回传了文件内容, 不能转给客户端; 不读内容直接关闭。
                logger.warning("github asset download returned %s instead of a redirect", resp.status)
                return None
        except urllib.error.HTTPError as e:
            if e.code in (301, 302, 303, 307, 308) and e.headers.get("Location"):
                return e.headers["Location"]
            logger.warning("github asset url failed %s", e.code)
            return None
    url = f"{API}/repos/{settings.github_repo}/contents/{_quote_path(github_path)}?ref={urllib.parse.quote(settings.github_branch)}"
    status, payload = _request("GET", url)
    if status == 200:
        return payload.get("download_url")
    logger.warning("github get failed %s: %s", status, payload.get("message"))
    return None


def delete(github_path: str, sha: str) -> bool:
    rel = _parse_release(github_path)
    if rel:
        # 删除 Release 会一并删除附件; 草稿没有 tag, 无需另删。
        status, _ = _request("DELETE", f"{API}/repos/{settings.github_repo}/releases/{rel[0]}")
        return status in (204, 404)
    if not sha:
        return False
    url = f"{API}/repos/{settings.github_repo}/contents/{_quote_path(github_path)}"
    body = {"message": f"shareweb: remove {github_path}", "sha": sha, "branch": settings.github_branch}
    status, _ = _request("DELETE", url, body)
    return status == 200
