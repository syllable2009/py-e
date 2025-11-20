from typing import Dict

from mydemo.spider.crawler_service import AbstractApiClient


class ZhiHuClient(AbstractApiClient):

    async def pong(self) -> bool:
        """
        用于检查登录态是否失效了
        Returns:
        """
        print(f"[ZhiHuClient.pong] Begin to pong zhihu...")
        ping_flag = False
        try:
            res = await self.get_current_user_info()
            if res.get("uid") and res.get("name"):
                ping_flag = True
                print(f"[ZhiHuClient.pong] Ping zhihu successfully")
            else:
                print(f"[ZhiHuClient.pong] Ping zhihu failed, response data: {res}")
        except Exception as e:
            print(f"[ZhiHuClient.pong] error:{e}")
        return ping_flag

    async def get_current_user_info(self) -> Dict:
        pass
