import asyncio
from urllib.parse import urljoin

from playwright.async_api import Page, expect, Locator, async_playwright


### 适用于playwright的page_util


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
async def open_url_on_new_page(page: Page, url: str, locator: Locator, timeout: float = 30000) -> Page:
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


# 只提取页面的元素，需要自行解析元素的属性["href", "src", "alt", "title"]
async def parse_list_element(locator: Locator, timeout: float = 30000):
    # 等待至少一个元素出现（避免空列表导致误判成功）
    try:
        await expect(locator.first).to_be_visible(timeout=timeout)
    except Exception as e:
        raise RuntimeError(f"Failed to find any element matching locator within {timeout}ms: {e}")

        # 获取所有匹配的元素数量
    count = await locator.count()
    # all_ = await locator.all()
    # print(f"{all_}")
    if count == 0:
        return []
    return [locator.nth(i) for i in range(count)]


# 只提取页面的第一个元素，需要自行解析元素的属性["href", "src", "alt", "title"]
async def parse_one_element(locator: Locator, timeout: float = 30000):
    # 等待至少一个元素出现（避免空列表导致误判成功）
    try:
        await expect(locator.first).to_be_visible(timeout=timeout)
    except Exception as e:
        raise RuntimeError(f"Failed to find any element matching locator within {timeout}ms: {e}")
    return locator.first


#  解析匹配出来的元素列表
async def parse_element(elements: list[Locator]) -> list[str]:
    result = []
    if not elements or len(elements) == 0:
        return result
    for e in elements:
        role = await e.get_attribute("role")
        tag = await e.evaluate("e => e.tagName.toLowerCase()")
        print(f"parse_element tag:{tag},role:{role}")
        extract = None
        if tag == "div":
            pass
        elif tag == "a":  # a标签
            extract = "href"
        elif tag == "link":
            extract = "href"
        elif tag == "img":
            extract = "src"
        else:
            pass
        if not extract:
            continue
        attribute = await e.get_attribute(extract)
        if attribute:
            result.append(attribute)
    return result


def get_full_url(base_url, raw_url):
    return urljoin(base_url, raw_url)


### 以下部分为测试代码

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
