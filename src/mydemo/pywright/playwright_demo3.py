from mydemo.pywright.chrome_util import ChromeBrowser
from playwright.sync_api import sync_playwright, Browser, BrowserContext, Page


#  测试弹出新页面

# 虽然你监听了 _context.on("page", handle_new_page)，但 在 handle_new_page 被触发时，这个新页面可能已经被关闭了
def handle_new_page(new_page: Page) -> None:
    """处理新页面的函数"""
    print(f"监听页面打开: {new_page.url}")
    # 可在这里添加自动操作逻辑
    new_page.wait_for_load_state("domcontentloaded")
    # 例如：自动截图或点击
    # new_page.click("#some-button")
    print(new_page.title())
    new_page.screenshot(path="/Users/jiaxiaopeng/opt/new_page.png")


def test1():
    cb: Browser = ChromeBrowser()
    page: Page = cb.get_new_page()
    _context: BrowserContext = page.context
    # 监听所有新页面创建事件，如果主流程太快关闭上下文，回调会失败
    page.goto("https://www.21voa.com/special_english/")
    # 注册监听方法，放在click之前
    _context.on("page", handle_new_page)
    # 触发新页面
    # page.click() 返回时，新页面可能刚被创建，但尚未加载完成，甚至可能还未触发。
    page.click("xpath=//*[@id='righter']/div[3]/ul/li[1]/a[2]")
    print(f"浏览器打开了: {len(_context.pages)}个页面")
    # 获取新页面
    all_pages = _context.pages
    latest_page = all_pages[-1]
    latest_page.wait_for_load_state("networkidle")
    print(f"浏览器打开了: {len(_context.pages)}个页面")
    page.screenshot(path="/Users/jiaxiaopeng/opt/playwright_demo3.png")


def test2():
    cb: Browser = ChromeBrowser()
    page: Page = cb.get_new_page()
    _context: BrowserContext = page.context
    page.goto("https://www.21voa.com/special_english/")
    # 触发新页面,为什么要在_context.wait_for_event之前
    # wait_for_event("page") 是在“等待未来发生的事件”，必须先触发动作（如点击），再等待结果。
    # 先下单（click 触发打开新页面），然后站在门口等快递（wait_for_event）→ 快递员（新页面）才会来
    page.click("xpath=//*[@id='righter']/div[3]/ul/li[1]/a[2]")
    print(f"浏览器打开了: {len(_context.pages)}个页面")
    # ✅ 等待新页面出现（最多等 10 秒）
    new_page = None
    try:
        new_page = _context.wait_for_event("page", timeout=50000)
    except Exception as e:
        print("❌ 未检测到新页面打开:", e)

    # ✅ 等待新页面加载完成
    new_page.wait_for_load_state("domcontentloaded")
    print(f"浏览器打开了: {len(_context.pages)}个页面")
    print(f"监听页面打开: {new_page.url}")
    print("新页面标题:", new_page.title())
    new_page.screenshot(path="/Users/jiaxiaopeng/opt/new_page.png")
    page.screenshot(path="/Users/jiaxiaopeng/opt/playwright_demo3.png")


def test3():
    cb: Browser = ChromeBrowser()
    page: Page = cb.get_new_page()
    _context: BrowserContext = page.context
    page.goto("https://www.21voa.com/special_english/")
    page.wait_for_load_state("networkidle")
    # 方式一：使用 wait_for_event（推荐）
    with _context.expect_page() as page_info:
        page.click("xpath=//*[@id='righter']/div[3]/ul/li[1]/a[2]")  # 触发新页面

    new_page = page_info.value  # 获取新页面对象
    new_page.wait_for_load_state("networkidle")  # 等待加载
    print("新页面 URL:", new_page.url)
    new_page.screenshot(path="/Users/jiaxiaopeng/opt/new_page.png")
    page.screenshot(path="/Users/jiaxiaopeng/opt/playwright_demo3.png")
    new_page.close()
    page.close()


if __name__ == "__main__":

    test1()




