import re
from playwright.sync_api import Page, expect, sync_playwright

with sync_playwright() as p:
    # 启动 Chromium 浏览器（无头模式默认开启）
    browser = p.chromium.launch(headless=False)  # headless=False 显示浏览器窗口
    page = browser.new_page()
    # 监听网络请求
    page.on('request', lambda request: print(request.url))

    page.on('response', lambda response: print(f"{response.url}-{response.status}"))

    # 拦截请求
    page.route('**/*.{png,jpg,jpeg}', lambda route: route.abort())

    # 修改响应
    page.route('**/api/data', lambda route: route.fulfill(
        status=200,
        body='{"message": "被我改了吧"}'
    ))

    # 打开网页
    goto = page.goto("https://playwright.dev/python/docs/library")

    # 获取页面标题
    print(page.title())

    # 截图
    page.screenshot(path="example.png")

    # 关闭浏览器
    browser.close()
