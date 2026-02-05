from fastapi import APIRouter
from mypy.api import product,users

api_router = APIRouter()

api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(product.router, prefix="/products", tags=["items"])