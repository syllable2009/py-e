import asyncio
from urllib.parse import urljoin

from playwright.async_api import Page, expect, Locator, async_playwright, BrowserContext


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


# 在当前页面查找元素，然后填充，否则超时报错
async def on_page_fill(page: Page, selector: str, value: str, timeout: float = 30000) -> Page:
    try:
        print(f"on_page_fill:{value}")
        # 等待元素出现在 DOM 中且可交互（推荐使用 "visible" 状态以确保可操作）
        await page.wait_for_selector(selector, state="visible", timeout=timeout)

        # 使用 fill() 方法：先清空再输入，适用于 <input> / <textarea>
        await page.fill(selector, value, timeout=timeout)

    except asyncio.TimeoutError as e:
        raise RuntimeError(
            f"在页面 {page.url} 上等待可填充元素 '{selector}' 超时（{timeout}ms）。"
            "可能原因：元素不存在、未加载完成、选择器错误，或该元素不可编辑。"
        ) from e
    except Exception as e:
        raise RuntimeError(
            f"在页面 {page.url} 上向元素 '{selector}' 填充文本 '{value}' 时发生错误: {e}"
        ) from e

    return page


# 在当前页面查找元素点击，否则超时报错
async def on_page_click(page: Page, selector: str, timeout: float = 30000) -> Page:
    try:
        # 等待元素出现在 DOM 中且可交互（visible + stable）
        await page.wait_for_selector(selector, state="visible", timeout=timeout)

        # 可选：进一步确保元素可见并可点击（避免被遮挡）
        element = page.locator(selector)
        # 在操作元素前自动将其滚动到可视区域内（如果尚未可见），从而避免因元素被遮挡或位于视窗外而导致的点击/填充失败。
        await element.scroll_into_view_if_needed(timeout=timeout)
        await element.click(timeout=timeout)

    except asyncio.TimeoutError as e:
        raise RuntimeError(
            f"在页面 {page.url} 上等待元素 '{selector}' 超时（{timeout}ms）。"
            "可能原因：页面未加载完成、选择器错误、元素动态延迟渲染等。"
        ) from e
    except Exception as e:
        raise RuntimeError(
            f"在页面 {page.url} 上点击元素 '{selector}' 时发生错误: {e}"
        ) from e
    return page


# 在当前页面查找元素点击弹出并返回新页面，否则超时报错
async def on_page_click_new_page(
        page: Page,
        url: str,
        selector: str,
        timeout: float = 30000
) -> Page:
    context: BrowserContext = page.context
    try:
        # 等待元素可见
        await page.wait_for_selector(selector, state="visible", timeout=timeout)

        # 监听新页面创建（设置 future 捕获新页面）
        new_page_future: asyncio.Future[Page] = asyncio.Future()

        def on_page_created(new_page: Page):
            if not new_page_future.done():
                new_page_future.set_result(new_page)

        # 注册监听器
        context.on("page", on_page_created)

        try:
            # 执行点击
            element = page.locator(selector)
            await element.scroll_into_view_if_needed(timeout=timeout)

            # 点击并等待可能的导航或新页面
            async with page.expect_popup() as popup_info:
                await element.click(timeout=timeout)
                # 如果有弹出页面，playwright 会自动捕获
                new_page = await popup_info.value
                return new_page

        except asyncio.TimeoutError:
            # expect_popup 超时，说明没有新页面
            pass
        finally:
            # 移除监听器避免内存泄漏
            context.remove_listener("page", on_page_created)

        # 如果没有弹出页面，则返回原页面
        return page

    except asyncio.TimeoutError as e:
        raise RuntimeError(
            f"在页面 {url} 上等待元素 '{selector}' 超时（{timeout}ms）。"
            "可能原因：页面未加载完成、选择器错误、元素动态延迟渲染等。"
        ) from e
    except Exception as e:
        raise RuntimeError(
            f"在页面 {url} 上点击元素 '{selector}' 时发生错误: {e}"
        ) from e


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
