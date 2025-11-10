from fastapi import APIRouter
from fastapi import FastAPI, HTTPException
from typing import List
from pydantic import BaseModel
from mydemo.core.result import success, fail
from mydemo.core.response_code_enum import BusinessCode

demo_router = APIRouter(prefix="/demo", tags=["用户"])


class UserCreate(BaseModel):
    name: str
    email: str


class UserOut(BaseModel):
    id: int
    name: str
    email: str


@demo_router.post("/add", response_model=UserOut)
def create_add(user: UserCreate):
    try:
        # 模拟创建用户
        new_user = UserOut(id=1, name=user.name, email=user.email)
        return success(data=new_user, msg=BusinessCode.USER_REPEAT.name)

    except Exception as e:
        return fail(msg=f"服务器内部错误: {str(e)}", code=BusinessCode.USER_REPEAT.code)
