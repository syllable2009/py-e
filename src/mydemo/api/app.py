from fastapi import FastAPI

from mydemo.api.user_api import user_router
app = FastAPI()
app.include_router(user_router)
@app.get("/")
def read_root():
    return {"Hello": "World"}


# sudo poetry run uvicorn mydemo.api.app:app --reload --host 0.0.0.0 --port 8000