import re, os, json
from pathlib import Path
from playwright.sync_api import sync_playwright, Browser, BrowserContext, Page, Response, Download, \
    TimeoutError as PlaywrightTimeoutError
import atexit

# 模块级单例：全局唯一的 Playwright + Browser
_playwright = None
_browser: Browser = None


def _init_browser():
    print("Initializing browser...")
    global _browser
    global _playwright, _browser
    if _browser is None:
        _playwright = sync_playwright().start()
        _browser = _playwright.firefox.launch(
            headless=False,
            # 可选：添加启动参数优化稳定性
            args=[
                "--disable-web-security",  # 禁用同源策略（Same-Origin Policy
                "--disable-features=SafeBrowsing",  # 禁用 Google 的 Safe Browsing（安全浏览） 功能
                "--safebrowsing-disable-download-protection",  # 禁用 下载保护（Download Protection）
                "--safebrowsing-disable-extension-blacklist",  # 允许安装被 Safe Browsing 黑名单禁止的扩展
                "--disable-blink-features=AutomationControlled",  # --disable-blink-features=AutomationControlled
                "--disable-popup-blocking",  # 禁用弹窗拦截。
                "--disable-extensions",  # 启动时不加载任何 Chrome 扩展。
                "--no-sandbox",  # 禁用 Chromium 的沙箱（sandbox）安全机制。
                "--disable-setuid-sandbox",  # 禁用 setuid 沙箱（Linux 特有
                "--disable-dev-shm-usage",  # 避免使用 /dev/shm 共享内存。
                "--disable-gpu",  # 禁用 GPU 硬件加速。
            ]
        )
        # 注册退出清理
        atexit.register(_cleanup)


def _cleanup():
    print("Closing browser...")
    global _playwright, _browser
    if _browser:
        _browser.close()
        _browser = None
    if _playwright:
        _playwright.stop()
        _playwright = None


# ChromeBrowser 类：轻量级，只管理 context 和 page
class ChromeBrowser:

    def __init__(self, cookie_path: str = None, viewport=None, user_agent=None):
        print("Initializing browser context...")
        _init_browser()  # 确保浏览器已启动
        self.cookie_path = Path(cookie_path) if cookie_path else None
        # 创建独立的上下文（隔离 Cookie、Storage 等）
        self._context: BrowserContext = _browser.new_context(
            viewport=viewport or {"width": 1920, "height": 1080},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            permissions=["geolocation", "notifications"],  # 模拟真实用户权限
            bypass_csp=True,  # 绕过内容安全策略（某些检测依赖 CSP）
            locale="zh-CN",
            timezone_id="Asia/Shanghai",
            accept_downloads=True
        )
        stealth_js = """
        // 覆盖常见自动化检测特征
        Object.defineProperty(navigator, 'webdriver', { get: () => false, });
        window.chrome = { runtime: {} };
        Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3, 4, 5] });
        Object.defineProperty(navigator, 'languages', { get: () => ['zh-CN', 'zh'] });
        Object.defineProperty(document, 'hidden', { get: () => false });
        Object.defineProperty(document, 'visibilityState', { get: () => 'visible' });

        // 防止检测到 Playwright 的 CDP 特征
        const originalQuery = window.navigator.permissions.query;
        window.navigator.permissions.query = (parameters) => (
            parameters.name === 'notifications'
                ? Promise.resolve({ state: Notification.permission })
                : originalQuery(parameters)
        );
        """

        self._context.add_init_script(stealth_js)
        # 如果 cookie_path 存在，加载状态
        if self.cookie_path and self.cookie_path.exists():
            self._context.add_cookies(self._load_cookies())
        # 注册退出时自动关闭（防止忘记调用 close）
        atexit.register(self.close)

    def _load_cookies(self):
        """从 storage_state 文件中提取 cookies（兼容 Playwright 格式）"""
        try:
            with open(self.cookie_path, "r", encoding="utf-8") as f:
                state = json.load(f)
                return state.get("cookies", [])
        except Exception as e:
            print(f"⚠️  加载 Cookie 失败: {e}")
            return []

    def _save_storage_state(self):
        """保存完整的 storage state（含 cookies, localStorage 等）"""
        if self.cookie_path:
            try:
                # Playwright 的 storage_state 包含 cookies + origins（localStorage）
                self._context.storage_state(path=str(self.cookie_path))
                print(f"✅ Cookie & storage 已保存到: {self.cookie_path}")
            except Exception as e:
                print(f"❌ 保存 Cookie 失败: {e}")

    def get_new_page(self) -> Page:
        return self._context.new_page()

    def close(self):
        """关闭当前上下文（不影响其他 ChromeBrowser 实例）"""
        print("Closing browser context...")
        if hasattr(self, '_context') and self._context:
            self._context.close()
            self._context = None

    def __del__(self):
        # 作为兜底（不保证一定执行，但配合 atexit 更安全）
        print("Deleting browser context...")
        self.close()

    def raise_response_status(self, response: Response):
        if response and response.ok:
            print(f"✅ 页面加载成功! 状态码: {response.status}")
        else:
            print(f"❌ 页面加载失败! 状态码: {response.status if response else '无响应'}")

    def download_file(self, page: Page, xpath: str, filename: str, download_path: str = "./downloads",
                      timeout: float = 30000):
        # 监听下载事件，没有触发下载会抛出异常
        try:
            # 监听下载事件（最多等待 timeout 毫秒）
            with page.expect_download(timeout=timeout) as download_info:
                page.click(xpath, timeout=timeout)

            # 如果成功捕获到下载
            download: Download = download_info.value
            # 创建下载目录
            download_dir = Path(download_path)
            download_dir.mkdir(parents=True, exist_ok=True)
            # 构造目标路径
            target_path = download_dir / filename
            download.save_as(target_path)
            # 保存文件（Playwright 会自动等待下载完成
            print(f"✅ 文件下载成功!: {target_path}")
            # 新页面下载也会触发
            # pages_after = len(context.pages)
            # new_page = context.pages[-1]  # 最后一个页面通常是新打开的
        except PlaywrightTimeoutError:
            # 点击后未触发下载（超时）
            print(f"❌ 超时：点击 {xpath} 后未检测到下载行为。")
            # 可选：截图或记录当前页面状态用于调试
            # page.screenshot(path=f"{download_path}/download_failed_{filename}.png")
            raise  # 或根据需求决定是否继续抛出异常
        except Exception as e:
            # 其他异常（如保存失败、文件系统错误等）
            print(f"❌ 下载过程中发生错误: {e}")
            raise
        print(f"✅ 文件下载成功!: {target_path}")

    # 获取最新打开的一个页面，通常用于获取弹出的新页面
    def get_latest_page(self) -> Page:
        all_pages = self._context.pages
        if len(all_pages) > 1:
            # 最后一个通常是最新打开的
            latest_page = all_pages[-1]
            latest_page.bring_to_front()
            return latest_page
        return None

if __name__ == "__main__":
    cb = ChromeBrowser(cookie_path="cookies.json")
    page = cb.get_new_page()
    response = page.goto("https://playwright.dev/python/docs/library", wait_until="domcontentloaded", timeout=60000)
    cb.raise_response_status(response)
    print(page.title())
    page.screenshot(path="example.png")
    cb._save_storage_state()
    page.close()
