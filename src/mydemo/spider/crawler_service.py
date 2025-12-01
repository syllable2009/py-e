import os
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, Optional, Any
from urllib.parse import urlparse

import httpx
from playwright.async_api import BrowserContext, BrowserType, Playwright, async_playwright
from sympy import false

from mydemo.spider import config


### 服务接口定义

class AbstractCrawler(ABC):

    def __init__(self) -> None:
        self.index_url = None
        self.user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
        self.cdp_manager = None
        self.client: AbstractApiClient = None

    async def do_with_playwright_cdp(self) -> None:
        pass

    async def do_with_playwright(self) -> None:
        print("I have nothing to do")

    async def start_with_http(self):
        pass

    async def start_with_playwright(self):
        playwright_proxy_format, httpx_proxy_format = None, None
        async with async_playwright() as playwright:
            self.chromium = playwright.chromium
            self.browser_context = await self.launch_browser(self.chromium, playwright_proxy_format, self.user_agent,
                                                             headless=False)
            await self.do_with_playwright()

    # @abstractmethod
    async def search(self):
        """
        search
        """
        pass

    # @abstractmethod
    async def launch_browser(self, chromium: BrowserType, playwright_proxy: Optional[Dict], user_agent: Optional[
        str],headless: bool = True) -> BrowserContext:
        home_path = Path(__file__).parent.resolve()
        user_data_dir = os.path.join(home_path, "browser_data", config.PLATFORM)
        browser_context = await chromium.launch_persistent_context(
            user_data_dir=user_data_dir,
            accept_downloads=True,
            headless=headless,
            proxy=playwright_proxy,  # type: ignore
            viewport={
                "width": 1920,
                "height": 1080
            },
            user_agent=user_agent or self.user_agent,
            channel="chrome",  # 使用系统的Chrome稳定版
        )
        return browser_context

    async def launch_browser_with_cdp(self, playwright: Playwright, playwright_proxy: Optional[Dict],
                                      user_agent: Optional[str], headless: bool = True) -> BrowserContext:
        """
        使用CDP模式启动浏览器（可选实现）
        :param playwright: playwright实例
        :param playwright_proxy: playwright代理配置
        :param user_agent: 用户代理
        :param headless: 无头模式
        :return: 浏览器上下文
        """
        # 默认实现：回退到标准模式
        return await self.launch_browser(playwright.chromium, playwright_proxy, user_agent, headless)


class AbstractLogin(ABC):

    @abstractmethod
    async def begin(self):
        pass

    @abstractmethod
    async def login_by_qrcode(self):
        pass

    @abstractmethod
    async def login_by_mobile(self):
        pass

    @abstractmethod
    async def login_by_cookies(self):
        pass


class AbstractStore(ABC):

    @abstractmethod
    async def store_content(self, content_item: Dict):
        pass

    @abstractmethod
    async def store_comment(self, comment_item: Dict):
        pass

    # TODO support all platform
    # only xhs is supported, so @abstractmethod is commented
    @abstractmethod
    async def store_creator(self, creator: Dict):
        pass


class AbstractStoreImage(ABC):
    # TODO: support all platform
    # only weibo is supported
    # @abstractmethod
    async def store_image(self, image_content_item: Dict):
        pass


class AbstractStoreVideo(ABC):
    # TODO: support all platform
    # only weibo is supported
    # @abstractmethod
    async def store_video(self, video_content_item: Dict):
        pass


class AbstractApiClient(ABC):

    def __init__(self):
        self.cookie_dict = None
        self.headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }

    async def update_cookies(self, browser_context: BrowserContext, index_url: str = None):
        if browser_context is None:
            print(f"update_cookies failed, browser context is None")
            return false
        if index_url is None:
            print(f"update_cookies failed, index_url is None")
            return false
        # 获取浏览器中的cookies
        storage = await browser_context.storage_state()
        # 从一个 URL（index_url）中提取其网络位置（netloc）部分，通常用于获取 域名（含端口，如果有）
        target_netloc = urlparse(index_url).netloc
        filtered_cookies = {}
        for c in storage["cookies"]:
            if target_netloc.endswith(c["domain"].lstrip(".")):
                filtered_cookies[c["name"]] = c["value"]
        self.cookies = filtered_cookies
        return True

    async def post(self, url, *,
                   params: Optional[Dict[str, Any]] = None,
                   data: Optional[Dict[str, Any]] = None,
                   json: Optional[Dict[str, Any]] = None,
                   cookies: Optional[Dict[str, str]] = None,
                   headers: Optional[Dict[str, str]] = None,
                   timeout: float = 30.0,
                   follow_redirects: bool = True,
                   **kwargs):
        params = params or {}
        data = data or {}
        json = json or None  # 显式允许 None
        cookies = cookies or self.cookie_dict
        headers = headers or self.headers

        async with httpx.AsyncClient(cookies=cookies, headers=headers, timeout=timeout,
                                     follow_redirects=follow_redirects, **kwargs) as client:
            response = await client.post(url, params=params, data=data, json=json, timeout=timeout)
            return response

    async def get(
            self,
            url: str,
            *,
            params: Optional[Dict[str, Any]] = None,
            cookies: Optional[Dict[str, str]] = None,
            headers: Optional[Dict[str, str]] = None,
            timeout: float = 30.0,
            follow_redirects: bool = True,
            **kwargs
    ) -> httpx.Response:
        """
        异步发送 GET 请求。

        Args:
            url: 目标 URL
            params: 查询参数（将被编码到 URL 中）
            headers: 自定义请求头
            timeout: 超时时间（秒）
            follow_redirects: 是否自动跟随重定向
            **kwargs: 透传给 httpx.AsyncClient 的其他参数（如 proxies, verify 等）

        Returns:
            httpx.Response 对象
        """
        params = params or {}
        cookies = cookies or self.cookie_dict
        headers = headers or self.headers

        async with httpx.AsyncClient(
                cookies=cookies,
                headers=headers,
                timeout=timeout,
                follow_redirects=follow_redirects,
                **kwargs
        ) as client:
            response = await client.get(
                url,
                params=params,
                timeout=timeout  # 可省略，因 client 已设置
            )
            return response
