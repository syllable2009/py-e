import asyncio

from crawlee import Request
from crawlee.crawlers import BeautifulSoupCrawler, BeautifulSoupCrawlingContext

crawler = BeautifulSoupCrawler(max_requests_per_crawl=10)
router = crawler.router


@router.handler("LIST")
async def handle_list_page(context: BeautifulSoupCrawlingContext) -> None:
    context.log.info(f"list:{context.request.url}")


@router.handler("DETAIL")
async def handle_detail_page(context: BeautifulSoupCrawlingContext) -> None:
    print(f"detail:{context.request.url}")


async def handle_default_page(context: BeautifulSoupCrawlingContext) -> None:
    print(f"default:{context.request.url}")


router.default_handler(handle_default_page)


async def beautiful_soup_crawler() -> None:
    await crawler.run([
        Request.from_url(url="https://crawlee.dev", label="LIST"),
        Request.from_url(url="https://crawlee.dev/python/docs/examples/crawl-specific-links-on-website",
                         label="DETAIL"),
        Request.from_url(url="https://crawlee.dev/python/docs/examples", label="HARD")
    ])


if __name__ == "__main__":
    asyncio.run(beautiful_soup_crawler())
