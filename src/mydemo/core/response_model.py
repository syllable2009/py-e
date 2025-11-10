from pydantic import BaseModel
from typing import Any, Optional, Generic, TypeVar
from datetime import datetime

T = TypeVar("T")


class ResponseModel(BaseModel, Generic[T]):
    code: int = 0
    msg: str = "success"
    data: Optional[T] = None
    time: str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")


class ErrorResponseModel(BaseModel):
    code: int = -1
    msg: str = "error"
    data: Optional[Any] = None
    time: str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
