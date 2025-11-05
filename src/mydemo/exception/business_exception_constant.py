from enum import Enum

class ExceptionCode(Enum):
    # 每个成员传入 (name, code) 元组
    OK = ("成功", 0)
    NOT_FOUND = ("未找到", 404)
    REPEAT = ("重复", 405)
    SERVER_ERROR = ("服务器错误", 500)

    # 自定义 __init__ 方法来解包元组
    def __init__(self, name: str, code: int):
        self.name_display = name  # 避免与 Enum 内置的 name 冲突
        self.code = code

    # 可选：自定义 __str__ 或 __repr__ 便于调试
    def __str__(self):
        return f"{self.name_display} ({self.code})"

