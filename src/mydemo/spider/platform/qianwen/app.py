import asyncio
import os
from pathlib import Path

from playwright.async_api import async_playwright, BrowserContext

from mydemo.spider.crawler_service import AbstractCrawler


class QianWenCrawler(AbstractCrawler):

    def __init__(self) -> None:
        super().__init__()
        self.index_url = "https://www.qianwen.com/chat/"

    async def _login(self):
        pass

    async def login_state(self):
        pass

    async def do_with_playwright(self):
        # 执行初始化脚本
        script_dir = Path(__file__).parent.parent.parent.resolve()
        script_path = os.path.join(script_dir, "libs/stealth.min.js")
        await self.browser_context.add_init_script(path=script_path)
        # 打开一个新页面
        self.context_page = await self.browser_context.new_page()
        # 路由到首页,等到页面加载完成
        await self.context_page.goto(self.index_url, wait_until="load")
        await asyncio.sleep(3)

        # 定位到输入框
        locator = self.context_page.get_by_placeholder("向千问提问")
        print(f"locator:{type(locator)},{locator}")
        await locator.fill("python的编辑工具比较")
        await asyncio.sleep(3)
