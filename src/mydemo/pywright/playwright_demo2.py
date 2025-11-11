import uuid
import requests
from mydemo.pywright.chrome_util import ChromeBrowser
from mydemo.utils.content_type_util import infer_file_type, infer_file_name
from mydemo.utils.download import save_bytes
import os
from urllib.parse import urlparse, urljoin

### 测试下载，不同的行为有不同的策略
# 点击后浏览器直接下载文件，用 page.expect_download()
# 点击后在新页面/当前页显示文件内容，提取 URL + requests.get().content】
# 点击后跳转到另一个 HTML 页面，

# 设置下载目录（绝对路径）
download_dir = os.path.abspath("/Users/jiaxiaopeng/opt/")
os.makedirs(download_dir, exist_ok=True)


def handle_route(route):
    response = route.fetch()
    content = response.body()
    print(response.url)
    suggested = response.headers.get("content-disposition", "")
    print(suggested)
    name = infer_file_name(response.url, "mp3")
    # 保存到文件
    with open(path := os.path.join(download_dir, name), "wb") as f:
        f.write(content)
        print(path)
    route.continue_()  # 或 abort() 如果不想加载到页面


# 按照资源类型请求拦截
def download1():
    cb = ChromeBrowser()
    page = cb.get_new_page()
    # 拦截 jpg/png/mp3 请求
    page.route("**/*.{jpg,jpeg,png,mp3}", handle_route)

    page.goto("https://www.21voa.com/special_english/wilbur-and-orville-wright-the-first-airplane-93397.html")
    page.wait_for_load_state("networkidle")

    # mp3_src = page.eval_on_selector("xpath=//*[@id='mp3']/source", "el => el.src")
    # print(f"mp3_src: {mp3_src}")
    page.click("xpath=//*[@id='mp3']")


# 真正下载，触发浏览器下载框
def download2():
    cb = ChromeBrowser()
    page = cb.get_new_page()
    page.goto("https://samples.mplayerhq.hu/JPEG-seq/")
    page.wait_for_load_state("networkidle")
    with page.expect_download() as download_info:
        page.click("xpath=/html/body/pre/a[6]")

    download = download_info.value
    # 注意：临时文件，结束后会删除
    # file_bytes = download.path().read_bytes()
    # # # 保存到指定路径
    save_path = os.path.join(download_dir, download.suggested_filename)
    download.save_as(save_path)
    print(f"文件已下载并保存到: {save_path}")


def handle_download(download):
    """处理下载事件（适用于 <a download> 或 Content-Disposition 触发的下载）"""
    suggested_filename = download.suggested_filename
    save_path = os.path.join(download_dir, suggested_filename)
    download.save_as(save_path)
    print(f"📥 下载完成: {save_path}")


def on_page_created(page):
    """当新页面创建时自动绑定下载和路由监听"""
    global new_page
    new_page = page
    print("监听页面创建:", page.url)

    # 👇 关键：为新页面绑定下载监听
    page.on("download", handle_download)

    # 👇 关键：为新页面绑定路由拦截（必须在 goto 前设置！）
    page.route("**/*.{mp3,jpg,jpeg,png}", handle_route)


# 新页面监听
new_page = None


def download3():
    cb = ChromeBrowser()
    page = cb.get_new_page()
    context = page.context
    # Playwright 中用于监听浏览器上下文新页面（Page）创建事件的机制（在点击前注册！）
    context.on("page", on_page_created)
    page.goto("https://samples.mplayerhq.hu/4khdr/")
    # <a> 链接是普通文件（如 .jpg, .mp3），浏览器不会打开新页面，只有 <a target="_blank"> 或 JS 弹出窗口才会创建新 Page
    page.click("xpath=/html/body/pre/a[15]")
    # 等待新页面加载完成
    if new_page:
        new_page.wait_for_load_state("networkidle")
        print("✅ 新页面加载完成")
    else:
        print("⚠️ 未检测到新页面")
        name = infer_file_name(page.url, "jpg")
        save_path = os.path.join(download_dir, name)
        page.wait_for_load_state("networkidle")
        page.screenshot(path=os.path.join(download_dir, "test.png"))
        # save_bytes(save_path, page.)


# 解析url,然后requests下载
def downlaod4():
    cb = ChromeBrowser()
    page = cb.get_new_page()
    page.goto("https://samples.mplayerhq.hu/JPEG-seq/")
    # 1. 提取链接的 href
    href = page.eval_on_selector("xpath=/html/body/pre/a[15]", "el => el.href")
    #     # 等待元素出现在 DOM 中（不一定可见）
    #     element = page.wait_for_selector(button_xpath, state="attached", timeout=10000)
    #     # 滚动到该元素（如果需要）
    #     element.scroll_into_view_if_needed(timeout=5000)
    #     # 再等待它变为可见（例如：不被遮挡、opacity > 0 等）
    #     element.wait_for_element_state("visible", timeout=10000)
    #     print("✅ 按钮已找到并可见，准备点击...")
    #     element.click()
    #     print(element.as_element())
    # 2. 补全绝对 URL（如果 href 是相对路径）
    full_url = urljoin(page.url, href)
    # 3. 复用 Playwright 的 cookies（防止 403）
    cookies = {c["name"]: c["value"] for c in page.context.cookies()}
    headers = {"User-Agent": page.evaluate("() => navigator.userAgent")}
    # 4. 用 requests 获取 bytes
    response = requests.get(full_url, cookies=cookies, headers=headers)
    response.raise_for_status()
    file_bytes = response.content  # 👈 这就是你要的 bytes！
    print(f"✅ 获取到 {len(file_bytes)} 字节")
    # 5. （可选）保存到文件
    filename = full_url.split("/")[-1].split("?")[0] or "downloaded_file"
    with open(f"./downloads/{filename}", "wb") as f:
        f.write(file_bytes)


def handle_response(response):
    # 检查是否是我们要下载的图片 URL
    print(f"url: {response.url}")
    if response.url is not None:
        content_type = response.headers.get("content-type", "")
        print(f"content_type: {content_type}")
        # 图片可下载
        if "image/" in content_type:
            try:
                image_data = response.body()
                filename = infer_file_name(response.url, content_type)
                save_path = '/Users/jiaxiaopeng/Downloads/' + filename
                # 保存
                save_bytes(save_path, image_data)
            except Exception as e:
                print(f"读取响应体失败: {e}")


if __name__ == "__main__":
    # handle_download(download=download, path=save_path)
    download3()
