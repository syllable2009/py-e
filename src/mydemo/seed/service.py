import os
from abc import ABC
from pathlib import Path
from typing import Optional, Dict

from playwright.async_api import async_playwright, BrowserType, BrowserContext

from mydemo.pywright.chrome_util import chromium_args
from mydemo.seed import config


class AbstractCrawler(ABC):

    def __init__(self) -> None:
        self.index_url = None
        self.user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
        # self.cdp_manager = None
        # self.client: AbstractApiClient = None
        self.brower_type = None
        self.browser = None
        self.browser_context = None

    async def do_with_playwright(self) -> None:
        print("I have nothing to do")

    async def start_with_playwright(self):
        playwright_proxy_format, httpx_proxy_format = None, None
        async with async_playwright() as playwright:
            self.brower_type = playwright.chromium
            self.browser_context = await self.launch_browser(self.brower_type, playwright_proxy_format, self.user_agent,
                                                             headless=config.HEADLESS)
            await self.do_with_playwright()

    async def launch_browser(self, chromium: BrowserType, playwright_proxy: Optional[Dict], user_agent: Optional[
        str], headless: bool = True) -> BrowserContext:
        # 配置浏览器数据
        home_path = Path(__file__).parent.resolve()
        user_data_dir = os.path.join(home_path, "browser_data", config.PLATFORM)
        self.browser_context = await chromium.launch_persistent_context(
            user_data_dir=user_data_dir,
            accept_downloads=True,
            headless=headless,
            proxy=playwright_proxy,  # type: ignore
            viewport={
                "width": 1920,
                "height": 1080
            },
            permissions=["geolocation"],
            user_agent=user_agent or self.user_agent,
            channel="chrome",  # 使用系统的Chrome稳定版
            args=chromium_args
        )
        # self.browser = await self.brower_type.launch(
        #     headless=False
        # )
        # self.browser_context = await self.browser.new_context()
        # 关键：删除 WebDriver 标志
        await self.browser_context.add_init_script("""
               Object.defineProperty(navigator, 'webdriver', {
                   get: () => undefined,
               });
               window.chrome = { runtime: {} };
               // 可选：伪造 plugins 和 mimeTypes
               Object.defineProperty(navigator, 'plugins', {
                   get: () => [1, 2, 3, 4, 5],
               });
               Object.defineProperty(navigator, 'mimeTypes', {
                   get: () => [1, 2, 3, 4, 5],
               });
           """)
        return self.browser_context
