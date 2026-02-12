import asyncio

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


async def handle_default_page(context: PlaywrightCrawlingContext) -> None:
    context.log.info(f"default:{context.request.url}")


router.default_handler(handle_default_page)



async def playwright_crawler() -> None:
    await crawler.run([
        Request.from_url(url="https://crawlee.dev", label="LIST"),
        Request.from_url(url="https://crawlee.dev/python/docs/examples/crawl-specific-links-on-website",
                         label="DETAIL"),
        Request.from_url(url="https://crawlee.dev/python/docs/examples", label="HARD")
    ])


if __name__ == "__main__":
    asyncio.run(playwright_crawler())