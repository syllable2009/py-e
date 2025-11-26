from urllib.parse import urlparse

from playwright.async_api import BrowserContext

from mydemo.spider.crawler_service import AbstractApiClient


class XCodeClient(AbstractApiClient):

    def __init__(self):
        self.cookies = {}

    # async def update_cookies(self, browser_context: BrowserContext):
    #     storage = await browser_context.storage_state()
    #     target_netloc = urlparse(self.index_url).netloc
    #     filtered_cookies = {}
    #     for c in storage["cookies"]:
    #         if target_netloc.endswith(c["domain"].lstrip(".")):
    #             filtered_cookies[c["name"]] = c["value"]
    #     self.cookies = filtered_cookies

    async def get_user_info(self, params={}):
        print(f"start logged in test")
        print(f"cookies:{self.cookies}")
        response = await self.post("https://www.yxzhi.com/wp-admin/admin-ajax.php", params=params, cookies=self.cookies)
        print(f"get_user_info,status_code:{response.status_code},content:{response.text}")
        return response