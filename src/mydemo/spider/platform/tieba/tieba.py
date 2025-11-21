from typing import Optional, Dict
from pathlib import Path
import os
from playwright.async_api import BrowserType, BrowserContext, async_playwright

from mydemo.spider.crawler_service import AbstractCrawler
from mydemo.spider.platform.tieba import config


class TiebaShuCrawler(AbstractCrawler):

    def __init__(self) -> None:
        self.index_url = "https://tieba.baidu.com"
        self.user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
        # self._page_extractor = TieBaExtractor()
        self.cdp_manager = None
        self.client = None

    async def start(self):
        """
        start crawler
        """
        # 浏览器代理和http请求代理
        playwright_proxy_format, httpx_proxy_format = None, None
        async with async_playwright() as playwright:
            chromium = playwright.chromium
            self.browser_context = await self.launch_browser(chromium, playwright_proxy_format, self.user_agent,
                                                             headless=False)
            # 获取当前脚本所在目录
            current_dir = os.getcwd()
            # 获取上上层目录
            upper_upper_dir = Path(current_dir).parent.parent
            # 路径拼接不能加/，否则为绝对地址
            join = os.path.join(upper_upper_dir, "libs/stealth.min.js")
            await self.browser_context.add_init_script(path=join)

        self.context_page = await self.browser_context.new_page()
        await self.context_page.goto(self.index_url)
        # 创建client，client封装了requests的操作
        self.client = None
        # 判断是否登录
        if not await self.loggedIn():
            # 登录，构建一个Login对象，执行登录操作

            # 更新cookie
            pass
        # 业务操作



    # 以json的形式保存cookie
    async def save_cookies(self, browser_context: BrowserContext):
        user_cookie_path = os.path.join(os.getcwd(), "browser_data", config.PLATFORM, "cookies.json")
        try:
            # Playwright 的 storage_state 包含 cookies + origins（localStorage）
            await browser_context.storage_state(path=str(user_cookie_path))
            print(f"✅ Cookie & storage 已保存到: {self.cookie_path}")
        except Exception as e:
            print(f"❌ 保存 Cookie 失败: {e}")

    async def load_cookies(self, browser_context: BrowserContext):
        return await browser_context.cookies()

    async def search(self):
        """
        search
        """
        pass

    async def launch_browser(self, chromium: BrowserType, playwright_proxy: Optional[Dict], user_agent: Optional[str],
                             headless: bool = True) -> BrowserContext:
        user_data_dir = os.path.join(os.getcwd(), "browser_data", config.PLATFORM)
        browser_context = await chromium.launch_persistent_context(
            user_data_dir=user_data_dir,
            accept_downloads=True,
            headless=headless,
            proxy=playwright_proxy,  # type: ignore
            viewport={
                "width": 1920,
                "height": 1080
            },
            user_agent=user_agent,
            channel="chrome",  # 使用系统的Chrome稳定版
        )
        return browser_context
