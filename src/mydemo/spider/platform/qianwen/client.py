import json
from typing import Dict, Union, Any

import httpx
from patchright.async_api import BrowserContext

from mydemo.spider.crawler_service import AbstractApiClient


class QianWenClient(AbstractApiClient):

    async def pong(self) -> bool:
        """
        用于检查登录态是否失效了
        Returns:
        """
        print(f"[QianWenClient.pong] Begin to pong zhihu...")
        ping_flag = False
        try:
            res = await self.get_current_user_info()
            if res.get("uid") and res.get("name"):
                ping_flag = True
                print(f"[QianWenClient.pong] Ping QianWenClient successfully")
            else:
                print(f"[QianWenClient.pong] Ping QianWenClient failed, response data: {res}")
        except Exception as e:
            print(f"[QianWenClient.pong] error:{e}")
        return ping_flag

    async def get_current_user_info(self) -> Dict:
        pass

    async def request(self, method, url, **kwargs):
        pass

    async def update_cookies(self, browser_context: BrowserContext):
        pass


async def request(method, url, **kwargs) -> Union[str, Any]:
    return_response = kwargs.pop('return_response', False)
    async with httpx.AsyncClient() as client:
        response = await client.request(method, url, timeout=30000, **kwargs)
    if response.status_code != 200:
        print(f"Requset Url: {url}, Request error: {response.text}")
    if return_response:
        return response.text
    try:
        data: Dict = response.json()
        if data.get("error"):
            print(f"Request error: {data}")
            raise Exception(data.get("error", {}).get("message"))
        return data
    except json.JSONDecodeError:
        print(f"Request error: {response.text}")
        raise Exception(response.text)


if __name__ == "__main__":
    import asyncio

    asyncio.run(QianWenClient().pong())
