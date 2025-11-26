from urllib.parse import urlparse

from playwright.async_api import BrowserContext

from mydemo.spider.crawler_service import AbstractApiClient


class XCodeClient(AbstractApiClient):

    def __init__(self):
        # 必须调用父类 __init__
        super().__init__()

    async def get_user_info(self, params={}):
        print(f"start get_user_info,params:{params}")
        response = await self.post("https://www.yxzhi.com/wp-admin/admin-ajax.php", params=params, cookies=self.cookies)
        print(f"get_user_info result,status_code:{response.status_code},content:{response.text}")
        return response