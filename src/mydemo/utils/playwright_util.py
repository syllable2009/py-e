import asyncio

from playwright.async_api import Page, expect, Locator, async_playwright


# 监听 popup 事件，自动关闭
async def on_close_popup(popup_page):
    # 可选：记录日志或做其他处理
    print(f"on_close_popup, closing: {popup_page.url}")
    await popup_page.close()


# 在当前页面打开url，如果有弹出的页面关闭
async def open_url_on_current_page(page: Page, url: str, locator: Locator, timeout: float = 30000):
    page.on("popup", on_close_popup)
    await page.goto(url)
    try:
        # 等待元素出现
        await expect(locator).to_be_visible(timeout=30000)
        # 点击元素
        await locator.click()
        return page
    except Exception as e:
        raise Exception(f"open_url_on_current_page target element did not visible within {timeout} ms: {e}")
    finally:
        # 清理监听器（避免内存泄漏）
        page.remove_listener("popup", on_close_popup)


# 在新的页面打开url，当前页面不关闭，新页面提到前台，返回新的页面
async def open_url_on_new_page(page: Page, url: str, locator: Locator, timeout: float = 30000):
    await page.goto(url)
    # 等待目标元素可见
    try:
        await expect(locator).to_be_visible(timeout=timeout)
    except Exception as e:
        raise Exception(f"open_url_on_new_page target element did not visible within {timeout} ms: {e}")

    # 准备等待 popup 事件
    popup_event = page.wait_for_event("popup", timeout=timeout)

    # 点击元素（应触发 popup）
    await locator.click()
    # 等待并获取 popup 页面
    try:
        popup_page = await popup_event
        return popup_page
    except asyncio.TimeoutError:
        raise Exception(f"open_url_on_new_page no popup appeared within {timeout} ms after clicking the element.")


async def t_open_url_on_current_page():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()

        # 假设有一个按钮点击后会 window.open()
        button_locator = page.get_by_text("电脑", exact=True).first

        try:
            popup = await open_url_on_current_page(
                page=page,
                url="https://www.yxzhi.com/",
                locator=button_locator,
                timeout=10000
            )
            print("Popup URL:", popup.url)
            await asyncio.sleep(5)
            await popup.close()
        except Exception as e:
            print("Error:", e)
        await browser.close()


async def t_open_url_on_new_page():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()

        # 假设有一个按钮点击后会 window.open()
        button_locator = page.get_by_text("卸载工具", exact=False).first

        try:
            popup = await open_url_on_new_page(
                page=page,
                url="https://www.yxzhi.com/windows",
                locator=button_locator,
                timeout=10000
            )
            print("Popup URL:", popup.url)
            await asyncio.sleep(5)
            await popup.close()
        except Exception as e:
            print("Error:", e)
        await browser.close()


if __name__ == "__main__":
    # 运行
    asyncio.run(t_open_url_on_current_page())
    asyncio.run(t_open_url_on_new_page())
