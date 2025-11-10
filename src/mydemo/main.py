from fastapi import FastAPI, Request, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import ValidationError
import traceback

from mydemo.api.user_api import user_router
from mydemo.api.demo_api import demo_router
app = FastAPI()

# === 全局异常处理器 ===
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """捕获所有未处理的异常"""
    # 生产环境不要暴露详细错误
    error_msg = "服务器内部错误"
    if app.debug:  # 仅在 debug 模式下显示详情
        error_msg = f"{type(exc).__name__}: {str(exc)}"
        print("".join(traceback.format_exception(type(exc), exc, exc.__traceback__)))

    return JSONResponse(
        status_code=500,
        content={
            "code": 5000,
            "msg": error_msg,
            "data": None
        }
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """处理手动抛出的 HTTPException"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "code": exc.status_code,
            "msg": exc.detail,
            "data": None
        }
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """处理请求参数校验失败（如 Pydantic 模型校验）"""
    return JSONResponse(
        status_code=422,
        content={
            "code": 4000,
            "msg": "请求参数格式错误",
            "data": exc.errors()  # 可选：返回具体错误字段
        }
    )

app.include_router(user_router)
app.include_router(demo_router)
@app.get("/")
def read_root():
    return {"Hello": "World"}

# sudo poetry run uvicorn mydemo.main:app --reload --host 0.0.0.0 --port 8000