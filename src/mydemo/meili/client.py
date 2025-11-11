# import asyncio
from typing import Optional
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
import meilisearch
from meilisearch.errors import MeilisearchApiError, MeilisearchCommunicationError

from mydemo.meili.settings import settings


class MeiliSearchClient:
    _sync_client: Optional[meilisearch.Client] = None
    # _async_client: Optional[meilisearch.AsyncClient] = None

    @classmethod
    def get_sync_client(cls) -> meilisearch.Client:
        if cls._sync_client is None:
            cls._sync_client = meilisearch.Client(
                url=settings.MEILISEARCH_URL,
                api_key=settings.MEILISEARCH_API_KEY,
                timeout=settings.MEILISEARCH_TIMEOUT,
            )
        return cls._sync_client

    # @classmethod
    # async def get_async_client(cls) -> meilisearch.AsyncClient:
    #     if cls._async_client is None:
    #         cls._async_client = meilisearch.AsyncClient(
    #             url=settings.MEILISEARCH_URL,
    #             api_key=settings.MEILISEARCH_API_KEY,
    #             timeout=settings.MEILISEARCH_TIMEOUT,
    #         )
    #     return cls._async_client


# 重试装饰器（用于网络波动）
@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=5),
    retry=retry_if_exception_type((MeilisearchCommunicationError, ConnectionError)),
)
def safe_meili_call(func, *args, **kwargs):
    return func(*args, **kwargs)
