import asyncio
from urllib.parse import urljoin

from crawlee import Request
from crawlee.crawlers import PlaywrightCrawler, PlaywrightCrawlingContext

crawler = PlaywrightCrawler(
    # Limit the crawl to max requests. Remove or increase it for crawling all links.
    max_requests_per_crawl=10,
    # Headless mode, set to False to see the browser in action.
    headless=False,
    # Browser types supported by Playwright.
    browser_type='chromium',
)

router = crawler.router


@router.handler("LIST")
async def handle_list_page(context: PlaywrightCrawlingContext) -> None:
    context.log.info(f"list:{context.request.url}")


@router.handler("DETAIL")
async def handle_detail_page(context: PlaywrightCrawlingContext) -> None:
    context.log.info(f"detail:{context.request.url}")
    await context.page.locator().text_content()


@router.handler("VOA_LIST")
async def handle_VOA_LIST_page(context: PlaywrightCrawlingContext) -> None:
    baseUrl = str(context.request.loaded_url)
    context.log.info(f"VOA_LIST:{context.request.url}")
    # 获取所有 li 元素
    li_elements = await context.page.locator(".list ul li").all()
    for li in li_elements:
        try:
            # 获取最后一个 <a> 元素的 href 属性
            last_a = li.locator("a").last
            href = await last_a.get_attribute("href")

            if not href or href.strip() in ("", "#", "javascript:void(0)"):
                continue  # 跳过无效链接

            # 转为绝对 URL（重要！）
            absolute_url = urljoin(baseUrl, href)

            context.log.info(f"Found article link: {absolute_url}")

            # 可选：将链接加入请求队列（如果你需要后续爬取）
            # await context.enqueue_links(urls=[absolute_url], label="VOA_ARTICLE")

            lrc_url = None
            #
            lrc_element = await li.locator("a.lrc").all()  # 关键：用 class="lrc" 定位
            if lrc_element:
                lrc_href = await lrc_element[0].get_attribute("href")
                if lrc_href and lrc_href.strip() not in ("", "#", "javascript:void(0)"):  # 检查是否存在
                    lrc_url = urljoin(baseUrl, lrc_href) if lrc_href else None
            if lrc_url:
                context.log.info(f"  └─ LRC: {lrc_url}")

        except Exception as e:
            context.log.warning(f"Failed to process li element: {e}")
            raise e
            continue


async def handle_default_page(context: PlaywrightCrawlingContext) -> None:
    context.log.info(f"default:{context.request.url}")


router.default_handler(handle_default_page)


async def playwright_crawler() -> None:
    await crawler.run([
        Request.from_url("https://www.21voa.com/", label="VOA_LIST")
        # Request.from_url(url="https://crawlee.dev", label="LIST"),
        # Request.from_url(url="https://crawlee.dev/python/docs/examples/crawl-specific-links-on-website",
        #                  label="DETAIL"),
        # Request.from_url(url="https://crawlee.dev/python/docs/examples", label="HARD")
    ])


if __name__ == "__main__":
    asyncio.run(playwright_crawler())
