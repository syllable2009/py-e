import atexit
import json
import random
from pathlib import Path
from typing import Optional, Dict, Any
import httpx

from playwright.async_api import (
    async_playwright,
    Browser as AsyncBrowser,
    BrowserContext as AsyncBrowserContext,
    Page as AsyncPage,
    Response,
    Download,
    TimeoutError as PlaywrightTimeoutError,
)

# ======================
# ### 异步chrome工具类 全局单例（异步安全）
# ======================
_playwright = None
_browser: Optional[AsyncBrowser] = None
_http_client: Optional[httpx.AsyncClient] = None


async def _init_browser():
    global _playwright, _browser
    if _browser is None:
        print("🚀 创建 Playwright 实例...")
        _playwright = await async_playwright().start()
        print("🌐 启动 Chromium 浏览器...")
        _browser = await _playwright.chromium.launch(
            headless=False,
            args=[
                "--disable-gpu",
                "--no-sandbox",
                "--disable-dev-shm-usage",
                "--no-first-run",
                "--no-default-browser-check",
                "--disable-infobars",
                "--window-position=0,0",
                "--ignore-certificate-errors",
                "--disable-blink-features=AutomationControlled",
                "--disable-renderer-backgrounding",
                "--lang=zh-CN",
                "--disable-web-security",
                "--disable-extensions",
            ],
        )


async def _cleanup():
    global _playwright, _browser, _http_client
    print("🧹 清理 Playwright 和浏览器...")
    if _http_client:
        await _http_client.aclose()
        _http_client = None
    if _browser:
        await _browser.close()
        _browser = None
    if _playwright:
        await _playwright.stop()
        _playwright = None


# ======================
# 异步 ChromeBrowser 类
# ======================
class ChromeBrowser:
    def __init__(
            self,
            cookie_path: Optional[str] = None,
            viewport: Optional[Dict[str, int]] = None,
            user_agent: Optional[str] = None,
    ):
        self.cookie_path = Path(cookie_path) if cookie_path else None
        self._context: Optional[AsyncBrowserContext] = None
        self._viewport = viewport or {"width": 1920, "height": 1080}
        self._user_agent = user_agent or (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        )
        # atexit.register(_cleanup)
        global _http_client
        if _http_client is None:
            # _http_client = httpx.AsyncClient(cookies=cookies_dict,
            #                                  headers=headers,
            #                                  timeout=httpx.Timeout(timeout),
            #                                  follow_redirects=True,
            #                                  http2=True,  # 启用 HTTP/2（更像浏览器）
            #                                  )
            pass

    async def __aenter__(self):
        await _init_browser()
        print("🆕 创建浏览器上下文...")

        context_kwargs = {
            "viewport": self._viewport,
            "user_agent": self._user_agent,
            "locale": "zh-CN",
            "timezone_id": "Asia/Shanghai",
            "bypass_csp": True,
            "accept_downloads": True,
            "permissions": ["geolocation", "notifications"],
        }

        # 如果存在 cookie 文件，直接加载完整 storage state
        if self.cookie_path and self.cookie_path.exists():
            context_kwargs["storage_state"] = str(self.cookie_path)

        self._context = await _browser.new_context(**context_kwargs)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

    async def close(self):
        if self._context:
            try:
                # 保存状态（如果指定了路径）
                if self.cookie_path:
                    await self._context.storage_state(path=str(self.cookie_path))
                    print(f"✅ 会话状态已保存到: {self.cookie_path}")
                await self._context.close()
            except Exception as e:
                print(f"⚠️ 关闭上下文时出错: {e}")
            finally:
                self._context = None

    async def get_new_page(self) -> AsyncPage:
        if not self._context:
            raise RuntimeError("Browser context not initialized. Use 'async with'.")

        page = await self._context.new_page()
        default_headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        await page.set_extra_http_headers(default_headers)
        return page

    async def get_cookies_dict(self):
        cookies_list = await self._context.cookies()
        cookies_dict = {cookie["name"]: cookie["value"] for cookie in cookies_list}
        return cookies_dict

    async def download_file(
            self,
            page: AsyncPage,
            xpath: str,
            filename: str,
            download_path: str = "./downloads",
            timeout: float = 30000,
    ):
        download_dir = Path(download_path)
        download_dir.mkdir(parents=True, exist_ok=True)
        target_path = download_dir / filename

        try:
            async with page.expect_download(timeout=timeout) as download_info:
                await page.click(xpath, timeout=timeout)

            download: Download = await download_info.value
            await download.save_as(target_path)
            print(f"✅ 文件下载成功: {target_path}")

        except PlaywrightTimeoutError:
            print(f"❌ 超时：点击 {xpath} 后未检测到下载行为。")
            raise
        except Exception as e:
            print(f"❌ 下载失败: {e}")
            raise

    async def get_latest_page(self) -> Optional[AsyncPage]:
        if not self._context:
            return None
        pages = self._context.pages
        return pages[-1] if len(pages) > 1 else None

    async def simulate_human_scroll(self, page: AsyncPage):
        """模拟人类滚动行为"""
        for _ in range(2):
            scroll_height = random.randint(200, 500)
            await page.evaluate(f"window.scrollBy(0, {scroll_height})")
            await page.wait_for_timeout(random.randint(500, 1200))

    def raise_response_status(self, response: Optional[Response]):
        if response and response.ok:
            print(f"✅ 页面加载成功! 状态码: {response.status}")
        else:
            status = response.status if response else "无响应"
            print(f"❌ 页面加载失败! 状态码: {status}")


# ======================
# 使用示例
# ======================
if __name__ == "__main__":
    import asyncio


    async def main():
        async with ChromeBrowser(cookie_path="cookies.json") as cb:
            page = await cb.get_new_page()
            response = await page.goto(
                "https://playwright.dev/python/docs/library",
                wait_until="domcontentloaded",
                timeout=60000,
            )
            cb.raise_response_status(response)
            print(await page.title())
            await page.screenshot(path="example_async.png")

            # 示例：模拟滚动
            await cb.simulate_human_scroll(page)

            cookies_dict = await cb.get_cookies_dict()
            for key, value in cookies_dict.items():
                print(f"{key}: {value}")


    asyncio.run(main())

    # 可选：程序退出前清理全局浏览器（非必须，因为通常只 run 一次）
    # asyncio.run(_cleanup())
