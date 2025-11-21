from playwright.async_api import Page


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
