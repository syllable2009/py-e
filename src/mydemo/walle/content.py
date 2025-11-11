from abc import ABC, abstractmethod
from typing import Optional


class MultimodalContent(ABC):
    """多模态内容基类"""
    type: str


class TextContent(MultimodalContent):
    """文本内容类"""
    content: str


class FileContent(MultimodalContent):
    """文件内容类"""
    file_id: str  # 文件ID
    file_name: str  # 文件名
    file_extension: str  # 文件后缀
    file_size: int = 0  # 文件大小，单位为字节
    file_pre_key: Optional[str] = None  # 文件预览key，非必需
