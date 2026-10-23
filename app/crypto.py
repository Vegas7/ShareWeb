"""AES-256-CBC 加密/混淆下载支持。

容器格式 (二进制, 命名为 SWE1)::

    MAGIC(4)  = b"SWE1"
    IV(16)    = 随机初始化向量
    BODY      = AES-256-CBC-PKCS7( HEADER + FILEBYTES )

其中::

    HEADER    = utf8(filename + "\n" + sha256_hex + "\n")

即原始文件名与 SHA-256 校验码被一起加密进密文里, 因此下载到的 .dat
文件本身不泄露任何可识别信息 (文件名/类型/大小特征均被抹去)。

密钥为每个分享独立生成的 32 字节随机数, 以 base64 形式展示给用户,
配套的 Windows PowerShell/.bat 解密脚本用同样的算法还原文件。

这里刻意选择 AES-256-CBC + PKCS7: 它是 Windows PowerShell 5.1 自带
[System.Security.Cryptography.Aes] 原生支持的模式, 无需安装任何东西即可解密;
AES-GCM 在 PowerShell 5.1 上不可用, 故不采用。
"""
from __future__ import annotations

import base64
import os
from typing import Iterator

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding

MAGIC = b"SWE1"
KEY_BYTES = 32          # AES-256
IV_BYTES = 16
_CHUNK = 1024 * 1024    # 1 MiB streaming chunks


def new_key_b64() -> str:
    """生成一个新的 32 字节随机密钥, 返回 base64 字符串。"""
    return base64.b64encode(os.urandom(KEY_BYTES)).decode("ascii")


def key_from_b64(key_b64: str) -> bytes:
    raw = base64.b64decode(key_b64)
    if len(raw) != KEY_BYTES:
        raise ValueError("invalid key length")
    return raw


def clean_filename(filename: str) -> str:
    """去掉换行 (会破坏加密容器 HEADER 的分隔, 也不能出现在 GitHub 路径里), 空名用 download.bin。"""
    return (filename or "download.bin").replace("\r", " ").replace("\n", " ").strip() or "download.bin"


def _header_bytes(filename: str, sha256_hex: str) -> bytes:
    return f"{clean_filename(filename)}\n{(sha256_hex or '').lower()}\n".encode("utf-8")


def container_size(filename: str, sha256_hex: str, file_len: int) -> int:
    """预先算出加密容器的确切字节数 (用于 Content-Length)。"""
    total = len(_header_bytes(filename, sha256_hex)) + int(file_len)
    pad = IV_BYTES - (total % IV_BYTES)   # PKCS7: 始终 1..16, 整除时补满一整块
    return len(MAGIC) + IV_BYTES + total + pad


def encrypt_stream(path: str, key_b64: str, filename: str, sha256_hex: str) -> Iterator[bytes]:
    """流式加密磁盘上的文件, 逐块产出容器字节, 适合直接喂给 StreamingResponse。"""
    key = key_from_b64(key_b64)
    iv = os.urandom(IV_BYTES)

    cipher = Cipher(algorithms.AES(key), modes.CBC(iv))
    encryptor = cipher.encryptor()
    padder = padding.PKCS7(algorithms.AES.block_size).padder()

    header = _header_bytes(filename, sha256_hex)

    yield MAGIC + iv
    yield encryptor.update(padder.update(header))

    with open(path, "rb") as f:
        while True:
            chunk = f.read(_CHUNK)
            if not chunk:
                break
            data = padder.update(chunk)
            if data:
                yield encryptor.update(data)

    tail = padder.finalize()
    out = encryptor.update(tail) + encryptor.finalize()
    if out:
        yield out
