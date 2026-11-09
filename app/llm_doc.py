"""给 AI agent / LLM 看的 API 说明 (英文 Markdown, 紧凑、可直接放进提示词)。

管理后台「API」页可以复制 / 下载; 持有密钥的 agent 也可以自己读取: GET /api/v1/llms.txt。
接口有变化时这里要同步修改 (面向人的说明在 web/admin.html)。
"""
from .config import settings
from .resumable import MAX_CHUNK_BYTES, RESUME_HOURS


def _size(n: int | None) -> str:
    if n is None:
        return "no limit"
    for unit, step in (("GB", 1024 ** 3), ("MB", 1024 ** 2), ("KB", 1024)):
        if n >= step:
            v = n / step
            return f"{v:.0f} {unit}" if v == int(v) else f"{v:.1f} {unit}"
    return f"{n} bytes"


_DOC = """# ShareWeb API

ShareWeb is a self-hosted file and text sharing service. Every share gets a 4-digit code and a link token; anyone with either can open and download it. Shares expire {days} days after creation unless an admin locks them.

- Base URL: `{base}/api/v1`
- Auth: send `Authorization: Bearer <API_KEY>` on every `/api/v1` request (`X-API-Key: <API_KEY>` also works). Missing or invalid key -> 401.
- Bodies are JSON unless noted. Errors are `{"detail": "<message>"}` with an HTTP status code.
- Limits on this server: file {max_file}, text {max_text}, upload chunk {max_chunk}.
- Downloading a file needs no key: `GET <share.download_url>` (`{base}/download/<token>`).

## Share object

Returned by every endpoint that returns a share.

```json
{
  "token": "string, ID in the share link",
  "code": "4-digit string",
  "type": "file | text",
  "filename": "string", "size": 0, "sha256": "hex", "mime_type": "string",
  "created_at": "ISO 8601 UTC", "expires_at": "ISO 8601 UTC, null while locked",
  "locked": false, "download_count": 0,
  "url": "share page for humans",
  "download_url": "direct file download, null for text shares",
  "owned": true,
  "text": "only for text shares, only from GET /shares/{token} and GET /codes/{code}"
}
```

`owned` is true when the share was created with the current key. Only owned shares are listed by `GET /shares` and can be deleted.

## Endpoints

### GET /info
-> `{"max_upload_bytes": int|null, "max_text_bytes": int, "retention_days": int, "max_chunk_bytes": int, "key": {"id": int, "name": str}}`

### POST /files
Upload a whole file in one request. Body: `multipart/form-data` with the file in field `file`.
-> 201 Share. Use the resumable upload below for large files or unreliable networks.

### POST /texts
Body: `{"text": "<non-empty string>"}` -> 201 Share (type `text`).

### POST /uploads  (resumable upload, step 1)
Body: `{"sha256": "<hex of the whole file>", "size": <bytes>, "filename": "<name>", "content_type": "<optional>", "upload_id": "<optional, to resume>"}`
- `{"exists": true, "share": Share}`: the server already has a file with this SHA-256. Done; the share may not be owned by you.
- `{"exists": false, "upload_id": "<id>", "offset": <bytes already received>, "max_chunk": <bytes>}`: continue with step 2 from `offset`.

### PUT /uploads/{upload_id}?offset=N  (resumable upload, step 2)
Body: raw bytes `file[N : N + chunk]` with chunk <= `max_chunk` (8 MB is a good size). N must equal the server's current offset.
- `{"done": false, "offset": <new offset>}`: send the next chunk from the new offset.
- `{"done": true, "share": Share}`: all bytes received and the SHA-256 verified.
- 409 `{"detail": "offset mismatch", "offset": <correct offset>}`: continue from the returned offset.
- 422 checksum mismatch: the data didn't match `sha256`; the upload is discarded, start over with a new POST /uploads.
To resume after an interruption, POST /uploads again with the same body plus `"upload_id"`; the reply has the offset to continue from. Unfinished uploads are kept {resume_hours} hours and can only be continued with the key that started them.

### GET /shares?limit=100&offset=0
Shares created with this key that are still valid, newest first. `limit` 1-1000.
-> `{"total": int, "limit": int, "offset": int, "items": [Share]}`

### GET /shares/{token}
-> Share (text shares include `text`). 404 if not found or expired.

### DELETE /shares/{token}
-> 204. 404 if not found, expired or not owned by this key. 409 if locked by the admin.

### GET /codes/{code}
Find a share by its 4-digit code. -> Share (text shares include `text`).
Wrong code -> 404 `{"detail": "invalid code", "fail_count": n}`. Repeated wrong codes from one IP -> 429 `{"cooldown_until": "<ISO time>"}`, then the IP is blacklisted (403 on every request).

## Status codes

200/201/204 success; 400 malformed request; 401 bad or missing key; 403 IP blacklisted; 404 not found / expired / not owned / wrong code; 409 offset mismatch or locked share; 413 file, text or chunk too large; 422 invalid parameters or checksum mismatch; 429 too many wrong codes; 507 server disk full.

## Recipes

Upload a file (small):
```
curl -H "Authorization: Bearer $KEY" -F "file=@report.pdf" {base}/api/v1/files
```

Upload a file (large, resumable):
1. Compute the SHA-256 and size of the file.
2. POST /uploads. If `exists` is true, use the returned share.
3. Loop: PUT /uploads/{upload_id}?offset=<offset> with the next chunk; on 409 jump to the returned offset; stop when `done` is true.

Share text:
```
curl -H "Authorization: Bearer $KEY" -H "Content-Type: application/json" -d '{"text": "hello"}' {base}/api/v1/texts
```

Get something a person shared with a code:
```
curl -H "Authorization: Bearer $KEY" {base}/api/v1/codes/4821
curl -OJ "<download_url from the reply>"
```

## Rules for agents

- Never guess or brute-force share codes. Use only codes a person gave you; a few wrong codes put the IP on cooldown and then on the blacklist.
- Keep the API key secret. Don't put it in share contents, filenames or URLs, and don't show it to users.
- After creating a share, give the user its `code` and `url`.
- Only delete shares you created (`owned: true`) and only when asked.
- On network errors during a resumable upload, POST /uploads again with `upload_id` and continue from the returned offset instead of starting over.
"""


def render() -> str:
    values = {
        "base": settings.public_base_url, "days": str(settings.retention_days),
        "max_file": _size(settings.max_upload_bytes), "max_text": _size(settings.max_text_bytes),
        "max_chunk": _size(MAX_CHUNK_BYTES), "resume_hours": str(RESUME_HOURS),
    }
    doc = _DOC
    for k, v in values.items():
        doc = doc.replace("{" + k + "}", v)
    return doc
