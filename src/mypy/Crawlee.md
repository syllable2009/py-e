# https://crawlee.dev/python/docs/introduction/scraping

# Crawlee 中有 3 种主要的爬行器类型可供使用
BeautifulSoupCrawler
ParselCrawler
PlaywrightCrawler
每个网络爬虫的基本思路是：访问一个网页，打开它，执行一些操作，保存结果，然后继续访问下一个网页，如此反复，直到完成任务

# 我应该去哪里？
所有爬虫都使用类实例Request来确定它们需要访问的位置
求存储在一个RequestQueue动态Request实例队列中
rq = await RequestQueue.open()
await rq.add_request('https://crawlee.dev')
crawler = BeautifulSoupCrawler(request_manager=rq)

# 我应该在那里做什么？
请求处理程序是一个用户自定义函数，爬虫会针对每个Request请求自动调用它RequestQueue。
它始终接收一个参数BasicCrawlingContext（或其子类）
@crawler.router.default_handler
async def request_handler(context: BeautifulSoupCrawlingContext) -> None:
        url = context.request.url
        title = context.soup.title.string if context.soup.title else ''
        context.log.info(f'The title of {url} is: {title}.')

await crawler.run() #更快的添加请求 await crawler.run(['https://crawlee.dev/'])

# 自定义处理程序，处理label
@crawler.router.handler('BLOG')
    async def blog_handler(context: BeautifulSoupCrawlingContext) -> None:
        context.log.info(f'Blog Processing {context.request.url}.')

# 寻找新链接
await context.enqueue_links() # 抓取操作enqueue_links会使用相同的主机名，不包括子域名。要将子域名包含在抓取范围内，请使用 ` strategyalias` 参数。
await context.enqueue_links(strategy='same-domain',)
await context.enqueue_links(strategy='all')
await context.enqueue_links(selector='a.article-link')
await context.enqueue_links(
            include=[Glob('https://someplace.com/**/cats')],
            exclude=[Glob('https://**/archive/**')],
        )
 await context.enqueue_links(
            selector='.collection-block-item',
            label='CATEGORY',) # 加入新链接并设置标签

# 在将请求加入队列之前对其进行转换
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
await context.enqueue_links(transform_request_function=transform_request)

# 解析数据
https://crawlee.dev/python/docs/introduction/scraping
title = await context.page.locator('.product-meta h1').text_content()
element = await context.page.locator('xpath=//h1[@class="title"]').text_content()

# 保存数据
Crawlee 提供了一个Dataset类，它对表格存储进行了抽象，使其非常适合存储抓取结果。

dataset = await Dataset.open()
data = {
            'manufacturer': manufacturer,
            'title': title,
            'sku': sku,
            'price': price,
            'in_stock': in_stock,
        }
await dataset.push_data(data)
简化为：
await context.push_data(data)

# 代码重构，路由，异常
单独的路由文件
router = Router[PlaywrightCrawlingContext]()
@router.default_handler
@router.handler('CATEGORY')
