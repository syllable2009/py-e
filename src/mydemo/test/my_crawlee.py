import asyncio

from crawlee import Glob, RequestOptions, RequestTransformAction, HttpHeaders
from crawlee.crawlers import PlaywrightCrawler, PlaywrightCrawlingContext, BeautifulSoupCrawler, \
    BeautifulSoupCrawlingContext
from crawlee.storages import KeyValueStore, RequestQueue, Dataset


def transform_request(
    request_options: RequestOptions,
) -> RequestOptions | RequestTransformAction:
    # Skip requests to PDF files
    if request_options['url'].endswith('.pdf'):
        return 'skip'

    if '/docs' in request_options['url']:
        # Add custom headers to requests to specific URLs
        request_options['headers'] = HttpHeaders({'Custom-Header': 'value'})

    elif '/blog' in request_options['url']:
        # Add label for certain URLs
        request_options['label'] = 'BLOG'

    else:
        # Signal that the request should proceed without any transformation
        return 'unchanged'

    return request_options

async def main() -> None:
    # example1
    rq = await RequestQueue.open()
    await rq.add_request('https://crawlee.dev')
    crawler = BeautifulSoupCrawler(request_manager=rq, max_requests_per_crawl=10, request_handler=None)
    dataset = await Dataset.open()

    @crawler.router.default_handler
    async def request_handler(context: BeautifulSoupCrawlingContext) -> None:
        # Extract <title> text with BeautifulSoup.
        # See BeautifulSoup documentation for API docs.
        url = context.request.url
        title = context.soup.title.string if context.soup.title else ''
        context.log.info(f'The title of {url} is: {title}.')
        # 感知上下文，默认将查找<a>包含特定属性的元素，href
        # 当然也可以覆盖，await context.enqueue_links(selector='a.article-link')
        await context.enqueue_links()
        # 自动处理重复，默认会使用相同的主机名，不包括子域名。
        await context.enqueue_links(strategy='same-domain')
        await context.enqueue_links(strategy='all')
        await context.enqueue_links(
            include=[Glob('https://someplace.com/**/cats')],
            exclude=[Glob('https://**/archive/**')],
        )
        await context.enqueue_links(transform_request_function=transform_request)
        data = {
            'manufacturer': 111,
            'title': "title",
            'sku': "sku",
            'price': 100,
            'in_stock': True,
        }
        await dataset.push_data(data)
        await context.push_data(data)
    await crawler.run()

    # example2
    crawler = PlaywrightCrawler(
        # Limit the crawl to max requests. Remove or increase it for crawling all links.
        max_requests_per_crawl=2,
        # Headless mode, set to False to see the browser in action.
        headless=False,
        # Browser types supported by Playwright.
        browser_type='chromium',
    )

    # Open the default key-value store.
    kvs = await KeyValueStore.open()

    # Define the default request handler, which will be called for every request.
    @crawler.router.default_handler
    async def request_handler(context: PlaywrightCrawlingContext) -> None:
        context.log.info(f'Processing {context.request.url} ...')

        # Capture the screenshot of the page using Playwright's API.
        screenshot = await context.page.screenshot()
        name = context.request.url.split('/')[-1]

        # Store the screenshot in the key-value store.
        await kvs.set_value(
            key=f'screenshot-{name}',
            value=screenshot,
            content_type='image/png',
        )

    # 每个爬虫都有一个隐式RequestQueue实例，直接run队列更快地添加请求
    await crawler.run(
        [
            'https://crawlee.dev',
            'https://apify.com',
            'https://example.com',
        ]
    )


if __name__ == '__main__':
    asyncio.run(main())