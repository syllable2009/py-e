import os
from dotenv import load_dotenv

# 自动从 .env 文件加载环境变量
load_dotenv(dotenv_path=".env")

# print(os.getenv("DEBUG"))

class Settings:
    MEILISEARCH_URL: str = os.getenv("MEILISEARCH_URL", "http://localhost:7700")
    MEILISEARCH_API_KEY: str = os.getenv("MEILISEARCH_API_KEY", "")
    MEILISEARCH_TIMEOUT: int = int(os.getenv("MEILISEARCH_TIMEOUT", "10"))

settings = Settings()
