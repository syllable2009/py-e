import asyncio
import json
import os
from pathlib import Path
from typing import Optional, Dict

from playwright.async_api import BrowserType, BrowserContext, async_playwright, expect

from mydemo.spider.crawler_service import AbstractCrawler, AbstractApiClient
from mydemo.spider.platform.xcode import config
from mydemo.spider.platform.xcode.client import XCodeClient
from mydemo.utils.page_util import *
from mydemo.utils.playwright_util import open_url_on_current_page, parse_list_element, parse_element, get_full_url


class XCodeCrawler(AbstractCrawler):

    def __init__(self) -> None:
        # self.index_url = "http://www.52im.net/"
        self.index_url = "https://www.yxzhi.com/"
        self.user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
        # self._page_extractor = TieBaExtractor()
        self.cdp_manager = None
        self.client: AbstractApiClient = None

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
            # 表示 Python 进程启动时所在的“工作目录”，不一定是脚本所在的目路
            # current_dir = os.getcwd()
            # print(f"current_dir={current_dir}")
            # 获取上层目录
            # upper_upper_dir = Path(current_dir)
            # 返回当前脚本的路径
            script_dir = Path(__file__).parent.parent.parent.resolve()
            print(f"script_dir={script_dir},type:{type(script_dir)}")
            # 路径拼接不能加/，否则为绝对地址
            script_path = os.path.join(script_dir, "libs/stealth.min.js")
            await self.browser_context.add_init_script(path=script_path)
            # 打开一个新页面
            self.context_page = await self.browser_context.new_page()
            # 路由到首页
            await self.context_page.goto(self.index_url)
            # 创建client，client封装了requests的操作
            await self.create_client(httpx_proxy_format)
            # 将浏览器cookies的刷新到client
            await self.client.update_cookies(self.browser_context, self.index_url)
            # 判断是否登录
            if not await self.login_state():
                # 登录，构建一个Login对象，执行登录操作
                # 登录
                await self.login()
                await self.client.update_cookies(self.browser_context)
                # 在检测
                logged_in = await self.login_state()
                if logged_in:
                    print(f"首次登录成功")
                else:
                    print(f"首次登录失败")
                    return
                # 更新cookie
            else:
                print(f"检测到已经是登录状态")

            # 在当前页打开电脑
            page: Page = await open_url_on_current_page(self.context_page, url=self.index_url,
                                                        locator=self.context_page.get_by_text(
                                                            "电脑",exact=True))
            await asyncio.sleep(3)

            element_list = await parse_list_element(
                page.locator('xpath=//*[@id="wrap"]/div[1]/main/section[2]/div[2]/ul[1]/li/div[2]/h3/a'))
            print(f"{element_list}")
            elements = await parse_element(element_list)
            print(f"{elements}")
            for e in elements:
                print(f"{get_full_url(self.index_url, e)}")
            if 1 == 1:
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

    # 通过页面登录
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

    # 判断是否登录
    async def login_state(self):
        params = {"action": "wpcom_is_login"}
        response = await self.client.get_user_info(params)
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

    async def task_1(self):
        # 从首页解析列表
        self.context_page.goto()
        # 返回上一页
        # await self.context_page.go_back()
        # 遍历列表，解析每个页
        pass