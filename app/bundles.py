"""多文件分享 (batches.py 打包出的 zip) 的内容浏览: 列出文件、单独取出某个文件、给图片生成缩略图。

建分享时把 zip 里的文件清单 (名字/大小/MIME) 存进 shares.bundle (JSON), 分享页据此显示图库和文件列表,
不必每次打开 zip。单个文件直接从 zip 里流式读出 (图片在 zip 里是 STORED, 读取几乎没有开销)。

缩略图 / 预览图按需生成并缓存在 data/thumbs/<storage_name>/ 下, 分享删除时一起删掉 (见 services._remove_stored)。
服务器内存只有 1GB 左右, 所以同一时间只生成一张, JPEG 用 draft 模式按缩小后的尺寸解码,
像素数过大的图片不生成 (前端改用原图或图标)。
"""
import json
import logging
import mimetypes
import os
import shutil
import threading
import zipfile
from pathlib import Path

from .config import settings

logger = logging.getLogger(__name__)

try:
    from PIL import Image, ImageOps
    try:
        import pillow_heif
        pillow_heif.register_heif_opener()
        _HEIF = True
    except Exception:  # 没装 pillow-heif: HEIC 只能下载, 不能预览
        _HEIF = False
    _PIL = True
except Exception:  # 没装 Pillow: 图库直接显示原图
    _PIL = _HEIF = False

# 浏览器能直接显示的图片
_WEB_EXT = {"jpg", "jpeg", "jfif", "pjpeg", "png", "apng", "gif", "webp", "avif", "bmp", "ico", "svg"}
# 浏览器 (多数) 不能显示, 需要服务器转成预览图的图片
_CONVERT_EXT = {"heic", "heif", "tif", "tiff"}
# 这些不交给 Pillow 生成缩略图 (矢量 / 图标), 缩略图直接用原图
_NO_THUMB_EXT = {"svg", "ico"}

THUMB_PX = 400       # 缩略图最长边 (网格里约 160-200 CSS px, 2x 屏幕也够清晰)
PREVIEW_PX = 2048    # HEIC/TIFF 转换后的预览图最长边
# 解码后超过这个像素数就不处理 (RGB 每像素 3 字节, 40M 像素约 120MB 内存)
_MAX_PIXELS = 40_000_000
# 缩略图只处理这个大小以内的图片文件
_MAX_SOURCE_BYTES = 80 * 1024 * 1024

_gen_lock = threading.Lock()


def _ext(name: str) -> str:
    return name.rsplit(".", 1)[-1].lower() if "." in name else ""


def describe(name: str, size: int, content_type: str | None) -> dict:
    """一个文件在清单里的描述。view: 图片在浏览器里怎么看 —— orig 原图 / preview 服务器转换后的预览图 / None 不是图片。"""
    ext = _ext(name)
    mime = (content_type or "").split(";")[0].strip().lower()
    if not mime or mime == "application/octet-stream":
        mime = mimetypes.guess_type(name)[0] or "application/octet-stream"
    if ext in _WEB_EXT:
        view = "orig"
    elif ext in _CONVERT_EXT:
        view = "preview"
    else:
        view = None
    return {"name": name, "size": size, "mime": mime, "view": view}


def dumps(entries: list[dict]) -> str:
    return json.dumps(entries, ensure_ascii=False, separators=(",", ":"))


def entries(row) -> list[dict] | None:
    """分享的文件清单 (不是多文件分享时为 None)。"""
    try:
        raw = row["bundle"]
    except (IndexError, KeyError):
        return None
    if not raw:
        return None
    try:
        data = json.loads(raw)
    except ValueError:
        return None
    return data if isinstance(data, list) else None


def public_entries(row) -> list[dict] | None:
    """给分享页用的清单: 加上 thumb (服务器能否生成缩略图), HEIC 等在不能转换时当作普通文件。"""
    items = entries(row)
    if items is None:
        return None
    out = []
    for e in items:
        view = e.get("view")
        ext = _ext(e.get("name") or "")
        convertible = _PIL and (ext not in ("heic", "heif") or _HEIF)
        if view == "preview" and not convertible:
            view = None
        thumb = bool(view) and _PIL and ext not in _NO_THUMB_EXT and convertible \
            and int(e.get("size") or 0) <= _MAX_SOURCE_BYTES
        out.append({"name": e.get("name"), "size": e.get("size"), "mime": e.get("mime"),
                    "view": view, "thumb": thumb})
    return out


class EntryNotFound(LookupError):
    pass


def entry_info(zip_path: Path, row, idx: int) -> tuple[dict, zipfile.ZipInfo]:
    """清单里第 idx 个文件及其在 zip 里的 ZipInfo (名字必须对得上, 防止取到清单以外的东西)。"""
    items = entries(row)
    if items is None or not 0 <= idx < len(items):
        raise EntryNotFound(idx)
    entry = items[idx]
    with zipfile.ZipFile(zip_path) as zf:
        infos = zf.infolist()
    if idx < len(infos) and infos[idx].filename == entry["name"]:
        return entry, infos[idx]
    for info in infos:
        if info.filename == entry["name"]:
            return entry, info
    raise EntryNotFound(idx)


def iter_entry(zip_path: Path, info: zipfile.ZipInfo, chunk: int = 256 * 1024):
    """流式读出 zip 里的一个文件 (同步生成器, Starlette 会放到线程池里跑)。"""
    with zipfile.ZipFile(zip_path) as zf, zf.open(info) as src:
        while True:
            data = src.read(chunk)
            if not data:
                break
            yield data


# ---------------------------------------------------------------- 缩略图

def _cache_dir(row) -> Path:
    name = Path(row["storage_path"]).name
    return settings.data_dir / "thumbs" / name


def cached(row, idx: int, kind: str) -> Path | None:
    """kind = thumb / preview; 已生成则返回文件路径。"""
    path = _cache_dir(row) / f"{idx}-{kind}.webp"
    return path if path.is_file() else None


class NoThumbnail(Exception):
    """这个文件生成不了缩略图 (格式不支持 / 太大 / 解码失败)。"""


def _save(im, path: Path, max_px: int, quality: int):
    im = im.copy()
    im.thumbnail((max_px, max_px), Image.LANCZOS)
    if im.mode not in ("RGB", "RGBA"):
        im = im.convert("RGBA" if "A" in im.getbands() or im.mode == "P" else "RGB")
    tmp = path.with_name(f".{path.name}.tmp")
    im.save(tmp, "WEBP", quality=quality, method=4)
    os.replace(tmp, path)


def generate(zip_path: Path, row, idx: int, kind: str) -> Path:
    """生成 (或取缓存) 缩略图 / 预览图。一次解码同时生成 thumb 和需要的 preview。"""
    hit = cached(row, idx, kind)
    if hit:
        return hit
    if not _PIL:
        raise NoThumbnail("pillow not installed")
    entry, info = entry_info(zip_path, row, idx)
    view = describe(entry["name"], entry.get("size") or 0, entry.get("mime")).get("view")
    if not view or _ext(entry["name"]) in _NO_THUMB_EXT:
        raise NoThumbnail("not a supported image")
    if kind == "preview" and view != "preview":
        raise NoThumbnail("original is viewable")
    if info.file_size > _MAX_SOURCE_BYTES:
        raise NoThumbnail("image file too large")
    with _gen_lock:
        hit = cached(row, idx, kind)  # 等锁期间可能已被别的请求生成
        if hit:
            return hit
        out_dir = _cache_dir(row)
        out_dir.mkdir(parents=True, exist_ok=True)
        try:
            with zipfile.ZipFile(zip_path) as zf, zf.open(info) as src:
                with Image.open(src) as im:
                    # JPEG: 按目标尺寸缩小解码 (最多 1/8), 大照片的内存和时间都省很多
                    im.draft("RGB", (PREVIEW_PX if view == "preview" else THUMB_PX,) * 2)
                    if im.width * im.height > _MAX_PIXELS:
                        raise NoThumbnail("too many pixels")
                    im.load()
                    im = ImageOps.exif_transpose(im)
                    if view == "preview":
                        _save(im, out_dir / f"{idx}-preview.webp", PREVIEW_PX, 85)
                    _save(im, out_dir / f"{idx}-thumb.webp", THUMB_PX, 78)
        except NoThumbnail:
            raise
        except Exception as exc:
            logger.info("thumbnail failed for %s #%d: %s", row["storage_path"], idx, exc)
            raise NoThumbnail(str(exc)) from exc
    hit = cached(row, idx, kind)
    if not hit:
        raise NoThumbnail("not generated")
    return hit


def warm(zip_path: Path, row):
    """建分享后在后台把所有缩略图先生成好 (打开分享页时网格就能直接显示)。"""
    for idx, e in enumerate(public_entries(row) or []):
        if not e["thumb"]:
            continue
        try:
            generate(zip_path, row, idx, "thumb")
        except (NoThumbnail, EntryNotFound):
            pass
        except Exception:
            logger.exception("thumbnail warm-up failed for %s #%d", row["storage_path"], idx)


def drop_cache(storage_path: str | None):
    """删除分享对应的缩略图缓存。"""
    if not storage_path:
        return
    path = settings.data_dir / "thumbs" / Path(storage_path).name
    root = (settings.data_dir / "thumbs").resolve()
    if path.resolve().parent == root and path.is_dir():
        shutil.rmtree(path, ignore_errors=True)
