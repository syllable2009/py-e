from playwright.async_api import BrowserContext

from mydemo.spider.crawler_service import AbstractApiClient


class XCodeClient(AbstractApiClient):

    def __init__(self):
        pass

    async def request(self, method, url, **kwargs):
        pass

    async def update_cookies(self, browser_context: BrowserContext):
        pass

    async def get_user_info(self, params={}, cookie_dict={}):
        print(f"start logged in test")
        response = await self.post("https://www.yxzhi.com/wp-admin/admin-ajax.php", params, cookie_dict)
        print(f"get_user_info,status_code:{response.status_code},content:{response.text}")
        return response