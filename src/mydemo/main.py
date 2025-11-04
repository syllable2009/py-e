from fastapi import FastAPI

from mydemo.api.user_api import user_router
app = FastAPI()
app.include_router(user_router)
@app.get("/")
def read_root():
    return {"Hello": "World"}