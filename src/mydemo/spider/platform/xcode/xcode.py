import asyncio
import json
import os
from pathlib import Path
from typing import Optional, Dict

from playwright.async_api import BrowserType, BrowserContext, async_playwright, expect

from mydemo.spider.crawler_service import AbstractCrawler
from mydemo.spider.platform.xcode import config
from mydemo.spider.platform.xcode.client import XCodeClient
from mydemo.utils.page_util import *


class XCodeCrawler(AbstractCrawler):

    def __init__(self) -> None:
        # self.index_url = "http://www.52im.net/"
        self.index_url = "https://www.yxzhi.com/"
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
            upper_upper_dir = Path(current_dir).parent
            print(f"upper_upper_dir={upper_upper_dir}")
            # 路径拼接不能加/，否则为绝对地址
            join = os.path.join(upper_upper_dir, "spider/libs/stealth.min.js")
            await self.browser_context.add_init_script(path=join)

            self.context_page = await self.browser_context.new_page()
            await self.context_page.goto(self.index_url)
            # 创建client，client封装了requests的操作
            await self.create_client(httpx_proxy_format)
            # 判断是否登录
            if not await self.loggedIn():
                # 登录，构建一个Login对象，执行登录操作
                await self.login()
                # 更新cookie
            if 1 == 1:
                logged_in = self.loggedIn()
                await logged_in
                print(logged_in)
                return
            tab = await open_link_in_new_tab(self.context_page, text='[书籍] 网络编程理论经典《TCP/IP详解》在线版')
            if tab is None:
                return
            await tab.bring_to_front()
            await asyncio.sleep(3)
            # 模拟处理业务
            xpath = "//*[@id='ID_bbs_subjects_p1']/li/a[2]"
            links = await page_analyze_link_by_xpath(tab, xpath)
            print(f"links={links}")
            await tab.close()
            # 当前页面提到前台
            await self.context_page.bring_to_front()
            await self.context_page.goto(
                url="https://www.21voa.com/special_english/wilbur-and-orville-wright-the-first-airplane-93397.html",
                wait_until="networkidle")

            link_locator = self.context_page.locator(
                "xpath=/html/body/div[4]/div[2]/div[3]/div[2]/div/div[1]/div[4]/div[3]/div/a[1]")
            await link_locator.wait_for(state="visible")
            await click_download(self.context_page, link_locator, save_path=None)
            await asyncio.sleep(3)
            if 1 == 1:
                return
            link_locator = self.context_page.get_by_role("link", name="社区")
            # 或者await self.context_page.locator('a:has-text("技术精选")').click()
            # 业务操作
            await link_locator.wait_for(state="visible")
            target = await link_locator.get_attribute('target')
            print(f"target={target}")
            if target == '_blank':
                # 监听新页面创建
                async with self.context_page.expect_popup() as popup_info:
                    await link_locator.click()
                new_page = await popup_info.value
                # 等待新页面加载完成
                await new_page.wait_for_load_state('networkidle')
                # 后续操作在 new_page 上进行
                print("新页面 URL:", await new_page.url())
                content = await new_page.content()
                await new_page.close()
            else:
                # 在当前页面处理
                pass
            await link_locator.click()
            await asyncio.sleep(3)
            await self.context_page.locator('a:has-text("网页端IM开发")').click()
            # 等待页面加载状态
            try:
                await self.context_page.wait_for_load_state('networkidle', timeout=10000)  # 10秒超时
            except Exception as e:
                print(f"页面加载超时:{e}")
            await asyncio.sleep(3)
            # 回退到上一页

            # 解析

    async def create_client(self, httpx_proxy_format):
        self.client = XCodeClient()

    async def safe_click_link(self, text: str, timeout: float = 10000):
        """
        安全点击包含指定文本的链接，并根据 target 属性处理新页面或当前页面。

        :param text: 链接中包含的可见文本
        :param timeout: 超时时间（毫秒），默认 10000ms = 10秒
        :return: 返回被加载的页面对象（可能是新页面或原页面）
        """
        link = self.context_page.locator(f'a:has-text("{text}")')

        # 等待链接可见，带超时
        await link.wait_for(state="visible", timeout=timeout)

        target = await link.get_attribute('target')

        if target == '_blank':
            # 监听弹出新页面，设置超时
            async with self.context_page.expect_popup(timeout=timeout) as popup_info:
                await link.click()
            new_page = await popup_info.value
            await new_page.wait_for_load_state('networkidle', timeout=timeout)
            return new_page
        else:
            href = await link.get_attribute('href')
            if href:
                new_page = await self.context.new_page()
                await new_page.goto(href)
                await new_page.wait_for_load_state('networkidle')
                # 后续操作在 new_page 上进行
                print("新页面标题:", await new_page.title())
                await new_page.bring_to_front()  # 将新页面带到前台（可选），默认不聚焦新标签页
                return new_page
            # 在当前页打开
            # await link.click()
            # await self.context_page.wait_for_load_state('networkidle', timeout=timeout)
            # return self.context_page

    async def search(self):

        pass

    async def _login(self):
        page = self.context_page
        await page.get_by_role("link", name="登录").click()
        print(f"start login")
        # await page.wait_for_selector('#user-avatar', state='visible')
        await expect(page.get_by_text("Just", exact=True)).to_be_visible(timeout=30000)

    async def login(self):
        try:
            # 设置总超时时间为 20 秒
            await asyncio.wait_for(self._login(), timeout=20.0)
            print("Login completed successfully.")
        except asyncio.TimeoutError:
            # 只有真正超时才报这个错
            raise Exception("Login process timed out after 20 seconds.")
        except Exception as e:
            raise e

    async def loggedIn(self):
        params = {"action": "wpcom_is_login"}
        storage = await self.browser_context.storage_state()
        # cookies = {c["name"]: c["value"] for c in storage["cookies"]}
        target_netloc = urlparse(self.index_url).netloc
        filtered_cookies = {}
        for c in storage["cookies"]:
            if target_netloc.endswith(c["domain"].lstrip(".")):
                filtered_cookies[c["name"]] = c["value"]
        print(f"self.client={self.client}")
        response = await self.client.get_user_info(params, filtered_cookies)

        loads = json.loads(response.text)
        return loads["result"] == 0

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
