import json
import os
import random
import traceback
from pathlib import Path
from typing import Optional
from mydemo.pywright.chrome_util import ChromeBrowser

page_url = None

def handle_response(response):
    url = response.url
    # if response.request.resource_type in ("xhr", "fetch"):
    if url == page_url:
        pass
    else:
        print(f"🎯 捕获到目标响应: {url}")
    # if target_url_pattern in url:
        # print(f"🎯 捕获到目标响应: {url}")
        # try:
        #     captured_bytes = response.body()  # ← 获取 bytes
        #     print(f"📥 响应大小: {len(captured_bytes)} bytes")
        # except Exception as e:
        #     print(f"❌ 获取 body 失败: {e}")

def force_download_route(route):
    url = route.request.url

    # 只处理图片请求（可根据实际扩展名调整）
    if url.endswith('pc'):
        print(f"🖼️ 拦截图片: {url}")
        # 获取原始响应
        response = route.fetch()
        # 添加 Content-Disposition: attachment 强制下载
        headers = response.headers
        headers["content-disposition"] = "attachment; filename=image.jpg"
        route.fulfill(
            response=response,
            headers=headers
        )
    else:
        # 其他请求正常放行
        print(f"pass: {url}")
        route.continue_()

# ==================== 使用示例 ====================
if __name__ == "__main__":
    # === 配置区 ===
    USERNAME = "Just"  # 必须与网页右上角显示的完全一致
    STORAGE_STATE_PATH = "login_state.json"  # 登录状态保存路径
    DOWNLOAD_PATH = "./downloads"  # 下载目录

    SHARE_URL = "https://pan.quark.cn/s/44b5f3e07407#/list/share/4eefd732cc244ab6ae1af8ebed4fc7c0"  # 替换为实际分享链接
    EXTRACT_CODE = "xxxx"  # 提取码
    FILE_NAME = "我的文件"  # 保存时的文件名（不含扩展名）

    # === 第一步：登录并保存状态（只需运行一次）===
    print("=" * 50)
    print("🔐 第一步：人工登录夸克网盘（请保持窗口可见）")
    print("=" * 50)

    cb = ChromeBrowser(cookie_path='./kuake.json')
    page = cb.get_new_page()
    # page.goto('https://pan.quark.cn/')
    # print(f"⏳ 请手动完成登录' ...")
    # try:
    #     # 等待页面出现用户名（表示已登录）
    #     page.wait_for_selector(f"text={USERNAME}", timeout=120000)
    #     print("✅ 检测到登录成功！")
    #     cb._save_storage_state()
    # except Exception as e:
    #     print("❌ 登录超时或未检测到用户名，请确保用户名正确且已完成登录。")
    #     raise e
    page.goto(SHARE_URL, timeout=30000)
    page.wait_for_load_state("networkidle")
    cb.simulation_operation(page)

    # 注册响应监听器
    page.on("response", handle_response)
    page_url = page.url
    page.locator("text=清理工具").first.click()
    page.route("**/*", force_download_route)
    with page.expect_download(timeout=30000) as download_info:
        print("🖱️ 点击下载按钮...")
        locator = page.locator("text=注意")
        print(f"{locator.get_attribute('title')}")
        locator.first.click()
    download = download_info.value
    if download.failure():
        raise Exception(f"下载失败: {download.failure()}")

    path = "/Users/jiaxiaopeng/Downloads"
    suggested_filename = download.suggested_filename
    join = os.path.join(path, suggested_filename)
    download.save_as(join)
    print(f"{join}")

