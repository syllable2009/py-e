import os, uuid
from urllib.parse import urlparse

IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp'}
VIDEO_EXTENSIONS = {'.mp4', '.avi', '.mov', '.mkv', '.flv', '.wmv', '.webm', '.m4v'}


def infer_file_type(content_type: str) -> str:
    if content_type:
        content_type = content_type.lower()
        if "png" in content_type:
            ext = ".png"
        elif "gif" in content_type:
            ext = ".gif"
        elif "webp" in content_type:
            ext = ".webp"
        elif "jpeg" in content_type:
            ext = ".jpeg"
        elif "jpg" in content_type:
            ext = ".jpg"
        else:
            ext = ""
    else:
        ext = ""
    return ext


def infer_file_name(url: str, content_type: str) -> str:
    if url is None:
        return ""
    parsed = urlparse(url)
    filename = os.path.basename(parsed.path)
    if not filename:
        filename = uuid.uuid4().hex + infer_file_type(content_type)
    if "." not in filename:
        ext = infer_file_type(content_type)
        filename = filename + ext
    return filename