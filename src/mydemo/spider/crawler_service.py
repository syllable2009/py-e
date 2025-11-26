from abc import ABC, abstractmethod
from typing import Dict, Optional, Any
from urllib.parse import urlparse

import httpx
from playwright.async_api import BrowserContext, BrowserType, Playwright
from sympy import false


### 服务接口定义

class AbstractCrawler(ABC):

    @abstractmethod
    async def start(self):
        """
        start crawler
        """
        pass

    @abstractmethod
    async def search(self):
        """
        search
        """
        pass

    @abstractmethod
    async def launch_browser(self, chromium: BrowserType, playwright_proxy: Optional[Dict], user_agent: Optional[str],
                             headless: bool = True) -> BrowserContext:
        """
        launch browser
        :param chromium: chromium browser
        :param playwright_proxy: playwright proxy
        :param user_agent: user agent
        :param headless: headless mode
        :return: browser context
        """
        pass

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
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"}

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
        cookies = cookies or {}
        headers = headers or {}

        async with httpx.AsyncClient(cookies=cookies, headers=headers, timeout=timeout,
                                     follow_redirects=follow_redirects, **kwargs) as client:
            response = await client.post(url, params=params, data=data, json=json, timeout=timeout)
            return response

    async def get(
            self,
            url: str,
            *,
            params: Optional[Dict[str, Any]] = None,
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
        cookies = self.cookie_dict or {}
        headers = headers or {}

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
