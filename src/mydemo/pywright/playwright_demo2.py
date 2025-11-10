import uuid
import requests
from mydemo.pywright.chrome_util import ChromeBrowser
from mydemo.utils.content_type_util import infer_file_type,infer_file_name
from mydemo.utils.download import save_bytes
import os
from urllib.parse import urlparse, urljoin


### 测试下载

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

def download1():
    cb = ChromeBrowser()
    page = cb.get_new_page()
    # 拦截 jpg/png/mp3 请求
    page.route("**/*.{jpg,jpeg,png,mp3}", handle_route)

    page.goto("https://www.21voa.com/special_english/wilbur-and-orville-wright-the-first-airplane-93397.html")
    page.wait_for_load_state("networkidle")

    # mp3_src = page.eval_on_selector("xpath=//*[@id='mp3']", "el => el.href")
    # print(f"mp3_src: {mp3_src}")
    page.click("xpath=//*[@id='mp3']")



def download2():
    cb = ChromeBrowser()
    page = cb.get_new_page()
    page.goto("https://www.21voa.com/special_english/wilbur-and-orville-wright-the-first-airplane-93397.html")
    page.wait_for_load_state("networkidle")
    with page.expect_download() as download_info:
        page.click("xpath=//*[@id='mp3']")

    download = download_info.value
    # # # 保存到指定路径
    save_path = os.path.join(download_dir, download.suggested_filename)
    download.save_as(save_path)

    print(f"文件已下载并保存到: {save_path}")

# 监听新页面（用于后续操作）
# new_page = None
# def on_page(page):
#     global new_page
#     new_page = page
#     print("监听页面创建:", page.url)
# # 注册
# cb._context.on("page", on_page)

def handle_download(download, path):
    file_path = path + download.suggested_filename
    print(f"触发下载准备保存: {file_path}")
    download.save_as(file_path)
    print(f"文件已下载并保存到: {file_path}")

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




# page.on("download", lambda download: handle_download(download, download_dir))?

# page.on("response", handle_response)
# page.goto("https://haowallpaper.com/homeViewLook/17854958797835648")
# page.goto("https://www.meilisearch.com/docs/learn/self_hosted/getting_started_with_self_hosted_meilisearch")
# Playwright 会自动等待元素出现并可交互
button_xpath = '//*[@id="content"]/span[11]/a'  # 👈 根据实际情况修改 XPath
# try:
#     # 等待元素出现在 DOM 中（不一定可见）
#     element = page.wait_for_selector(button_xpath, state="attached", timeout=10000)
#
#     # 滚动到该元素（如果需要）
#     element.scroll_into_view_if_needed(timeout=5000)
#
#     # 再等待它变为可见（例如：不被遮挡、opacity > 0 等）
#     element.wait_for_element_state("visible", timeout=10000)
#
#     print("✅ 按钮已找到并可见，准备点击...")
#     element.click()
#
#     print(element.as_element())
#
# except TimeoutError:
#     print("❌ 超时：未找到按钮或按钮不可见")

# href = page.get_attribute(button_xpath, "href")
# print(href)
# full_url = urljoin(page.url, href)
# print(full_url)
# cookies = {c["name"]: c["value"] for c in cb._context.cookies()}
# cb._context.storage_state(path="cookies.json")
# resp = requests.get(full_url, cookies=cookies, headers={"Referer": page.url})
# with open("/Users/jiaxiaopeng/Downloads/movies.json" , "wb") as f:
#     f.write(resp.content)
# print("✅ 通过 requests 下载成功")

# page.wait_for_timeout(1000)  # 给一点时间让新页面触发
# page.click(button_xpath)
# with page.expect_download(timeout=10000) as download_info:  # 👈 关键：监听下载
#     page.click(button_xpath)

# if new_page is None:
#         print("未检测到新页面打开！")
#         # 在当前页下载
#         with page.expect_download() as download_info:
#             page.click(button_xpath)
# else:
#     # 等待新页面加载（可选）
#     new_page.wait_for_load_state("domcontentloaded")
#     # 假设新页面有一个“确认下载”按钮（根据实际情况调整）
#     confirm_button_xpath = '//button[contains(text(), "确认下载")]'
#     # 尝试查找确认按钮，如果存在就点击；否则认为会自动下载
#     with new_page.expect_download(timeout=30000) as download_info:
#         if new_page.is_visible(confirm_button_xpath):
#             new_page.click(confirm_button_xpath)
#         else:
#             # 如果没有确认按钮，可能已自动开始下载
#             # Playwright 会自动捕获后续的下载
#             pass


# 获取下载对象
#


# if new_page is not None:
#     # 关闭新页面
#     new_page.close()
# 关闭当前页
# page.close()


if __name__ == "__main__":
    # handle_download(download=download, path=save_path)
    download1()