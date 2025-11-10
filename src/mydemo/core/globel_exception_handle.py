from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    return fail(msg=f"未知错误: {str(exc)}", code=5000)

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    return fail(msg="请求参数校验失败", code=4000, data=exc.errors())