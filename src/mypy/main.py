from fastapi import FastAPI
import uvicorn
from mypy.api.routes import api_router
from mypy.service.crawlee_service import beautiful_soup_crawler


app = FastAPI(
    title="My FastAPI App",
    description="Generated with Poetry",
    version="0.1.0"
)

# 挂载 API 路由
app.include_router(api_router, prefix="/api/v1")

@app.get("/")
async def read_root():
    await beautiful_soup_crawler()
    return "OK"

@app.get("/items/{item_id}")
def read_item(item_id: int, q: str = None):
    return {"item_id": item_id, "q": q}


# 直接运行脚本时启动
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)