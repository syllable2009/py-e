import uuid

from playwright.async_api import Page, Download
import os
from urllib.parse import urljoin, urlparse
import datetime


# xpath解析页面的链接
async def page_analyze_link_by_xpath(page: Page, xpath: str, timeout: float = 10000):
    try:
        link_elements = page.locator(f"xpath={xpath} >> visible=true")
        # 等待至少有一个匹配的元素被添加到页面
        await link_elements.first.wait_for(state="visible", timeout=timeout)
        # 获取元素总数
        count = await link_elements.count()
        hrefs = []
        for i in range(min(count, 500)):  # 防止无限循环（安全上限）
            href = await link_elements.nth(i).get_attribute("href")
            if href and href.strip():
                hrefs.append(href.strip())
        # 转为绝对 URL（可选但推荐）
        from urllib.parse import urljoin
        base_url = page.url
        from urllib.parse import urljoin
        absolute_urls = [urljoin(base_url, h) for h in hrefs]
        # 去重并保持顺序
        return list(dict.fromkeys(absolute_urls))
    except Exception as e:
        print(f"page_analyze_link_by_xpath error: {e}")
    return []


# 模拟右键在新页面打开链接
async def open_link_in_new_tab(page: Page, text: str, timeout: float = 10000):
    """
    强制在新标签页中打开包含指定文本的链接（模拟右键 -> 在新标签页中打开）

    :param page: 当前页面对象
    :param text: 链接中包含的可见文本
    :param timeout: 超时时间（毫秒）
    :return: 新页面对象，失败返回 None
    """
    try:
        # 1. 定位链接
        link = page.locator(f'a:has-text("{text}")')
        # 2. 等待链接可见
        await link.wait_for(state="visible", timeout=timeout)
        # target = await link.get_attribute('target')

        count = await link.count()
        if count == 0:
            raise ValueError(f"未找到包含文本 '{text}' 的链接")
        elif count > 1:
            print(f"找到 {count} 个匹配链接，将使用第一个")
            link = link.first

        # 3. 获取 href
        href = await link.get_attribute('href')
        if not href or not href.strip():
            raise ValueError(f"链接文本 '{text}' 对应的 href 为空或不存在")

        # 4. 创建新页面（新标签页）
        new_page = await page.context.new_page()

        # 5. 在新页面中打开链接，并设置超时
        await new_page.goto(href, timeout=timeout)
        await new_page.wait_for_load_state('networkidle', timeout=timeout)

        return new_page

    except TimeoutError:
        print(f"open_link_in_new_tab timeout: 超时 {timeout}ms 内未完成操作")
    except Exception as e:
        print(f"open_link_in_new_tab error: {e}")
    return None


# 点击打开新页面下载
async def click_new_page_download():
    pass


# 通过导航到下载链接触发下载（适用于直接文件链接）
async def download_link(page: Page, url: str, save_path: str = None):
    # 通过导航到下载链接触发下载（适用于直接文件链接）
    async with page.expect_download(timeout=30000) as download_info:
        await page.goto(url, wait_until="domcontentloaded")
    download: Download = await download_info.value
    suggested_filename = await download.suggested_filename()
    if not suggested_filename:
        suggested_filename = os.path.basename(urlparse(url).path) or uuid.uuid4().hex
    # 5. 保存文件
    if save_path is None:
        save_path = os.getcwd()  # 或使用临时目录
    file_path = os.path.join(save_path, suggested_filename)
    await download.save_as(file_path)
    print(f"文件已保存至: {file_path}")


# 点击触发下载
async def click_download(page: Page, selector: str, save_path: str = None):
    """
    点击按钮并处理下载

    :param page: 当前页面
    :param button_selector: 按钮的选择器（如 'button#download-btn'）
    :param save_path: 保存路径（如 './books/tcpip.pdf'），若为 None 则返回临时路径
    :return: 下载文件的完整路径
    """
    popups = []  # 用于收集弹出页面

    def handle_popup(popup_page):
        popups.append(popup_page)

    # 监听 popup 事件
    page.on("popup", handle_popup)

    try:
        # 1. 监听 download 事件
        async with page.expect_download() as download_info:
            # 2. 点击按钮（触发下载） await page.click(link_locator)
            await selector.click()
        # 3. 获取 download 对象
        download: Download = await download_info.value

        # 关闭所有弹出页面
        for popup in popups:
            try:
                await popup.close()
                print(f"已关闭弹出页面: {popup.url}")
            except Exception as e:
                print(f"关闭 popup 失败: {e}")

        # 4. 获取建议的文件名（可选）
        suggested_filename = await download.suggested_filename()
        if not suggested_filename:
            suggested_filename = os.path.basename(urlparse(download.page.url).path) or uuid.uuid4().hex
        print(f"下载文件名: {suggested_filename}")
        # 5. 保存文件
        if save_path is None:
            save_path = os.getcwd()  # 或使用临时目录
        file_path = os.path.join(save_path, suggested_filename)
        await download.save_as(file_path)
        print(f"文件已保存至: {file_path}")
        return save_path
    except Exception as e:
        print(f"click_download error: {e}")
    finally:
        # 移除监听器（避免内存泄漏）
        page.remove_listener("popup", handle_popup)
    return None
