import asyncio

from mydemo.spider.crawler_service import AbstractCrawler


class SunoCrawler(AbstractCrawler):

    def __init__(self):
        super().__init__()
        self.index_url = "https://suno.com/"

    async def do_with_playwright(self) -> None:
        print(f"SunoCrawler start")
        # 打开一个新页面
        self.context_page = await self.browser_context.new_page()
        await self.context_page.goto(self.index_url, wait_until="load")
        await asyncio.sleep(3)


