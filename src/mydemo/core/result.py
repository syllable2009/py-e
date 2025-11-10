from fastapi.responses import JSONResponse
from typing import Any, Optional
from .response_model import ResponseModel, ErrorResponseModel


def success(data: Any = None, msg: str = "success", code: int = 0) -> JSONResponse:
    return JSONResponse(
        content=ResponseModel(code=code, msg=msg, data=data).model_dump(),
        status_code=200
    )


def fail(msg: str = "error", code: int = -1, data: Any = None) -> JSONResponse:
    return JSONResponse(
        content=ErrorResponseModel(code=code, msg=msg, data=data).model_dump(),
        status_code=200  # 注意：业务错误仍返回 200，由 code 区分
    )
