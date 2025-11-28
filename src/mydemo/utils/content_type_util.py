import os, uuid
from urllib.parse import urlparse, unquote

IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp'}
VIDEO_EXTENSIONS = {'.mp4', '.avi', '.mov', '.mkv', '.flv', '.wmv', '.webm', '.m4v'}

# 更准确的 MIME 映射（可按需扩展）
MIME_TO_EXT = {
    # Images
    'image/png': '.png',
    'image/gif': '.gif',
    'image/webp': '.webp',
    'image/jpeg': '.jpg',
    'image/jpg': '.jpg',
    'image/bmp': '.bmp',
    'image/tiff': '.tiff',
    'image/x-icon': '.ico',
    'image/svg+xml': '.svg',
    # Videos
    'video/mp4': '.mp4',
    'video/avi': '.avi',
    'video/quicktime': '.mov',
    'video/x-matroska': '.mkv',
    'video/x-flv': '.flv',
    'video/x-ms-wmv': '.wmv',
    'video/webm': '.webm',
    'video/mp4v-es': '.m4v',
    # Others
    'application/pdf': '.pdf',
    'text/plain': '.txt',
    'application/zip': '.zip',
    'application/x-gzip': '.gz',
}


def infer_file_type(content_type: str) -> str:
    if not content_type:
        return None
    # 提取主类型（去掉 charset 等参数）
    ct = content_type.split(';')[0].strip().lower()
    if ct in MIME_TO_EXT:
        return MIME_TO_EXT[ct]
    return None


def infer_file_name(url: str = None, content_type: str = None) -> str:
    file_name = None
    file_ext = None
    if not content_type:
        file_ext = infer_file_type(content_type)
    if url is not None:
        parsed_url = urlparse(url)
        basename = os.path.basename(unquote(parsed_url.path))
        if basename:
            name, ext = os.path.splitext(basename)
            if name:
                # 清理非法字符（Windows
                file_name = "".join(c for c in name if c.isalnum() or c in "._-")
            if not file_ext and ext:
                file_ext = ext.lower()
        else:
            file_ext = infer_file_type(content_type)

    if not file_name:
        file_name = uuid.uuid4().hex
    if not file_ext:
        file_ext = ".file"
    return file_name + file_ext
