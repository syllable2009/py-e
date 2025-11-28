import uuid


from mydemo.pywright.chrome_util import ChromeBrowser
from mydemo.utils.content_type_util import infer_file_name
from mydemo.utils.download_util import save_bytes
import os
from urllib.parse import urlparse


# 设置下载目录（绝对路径）
download_dir = os.path.abspath("/Users/jiaxiaopeng/Downloads")
# os.makedirs(download_dir, exist_ok=True)


cb = ChromeBrowser(cookie_path="cookies.json")


# 监听新页面（用于后续操作）
# new_page = None
# def on_page(page):
#     global new_page
#     new_page = page
#     print("监听页面创建:", page.url)
# # 注册
# cb._context.on("page", on_page)

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


page = cb.get_new_page()
page.on("response", handle_response)
# page.goto("https://haowallpaper.com/homeViewLook/17854958797835648")
page.goto("https://images.pexels.com/photos/807598/pexels-photo-807598.jpeg")
# Playwright 会自动等待元素出现并可交互
# button_xpath = '//*[@id="main-content"]/div/div/div[1]/div[2]/div[2]/div[1]/div'  # 👈 根据实际情况修改 XPath
# page.wait_for_selector(button_xpath, state='visible')
# page.wait_for_timeout(1000)  # 给一点时间让新页面触发
# page.click(button_xpath)
# with page.expect_download() as download_info:  # 👈 关键：监听下载
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
# download = download_info.value
# # 保存到指定路径
# save_path = os.path.join(download_dir, download.suggested_filename)
# download.save_as(save_path)
#
# print(f"文件已下载并保存到: {save_path}")

# if new_page is not None:
#     # 关闭新页面
#     new_page.close()
# 关闭当前页
page.close()
