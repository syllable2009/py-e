from fastapi import APIRouter

user_router = APIRouter()

@user_router.get("/user")
def user_root():
    return {"user": "ok"}