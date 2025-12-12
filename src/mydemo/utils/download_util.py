import aiofiles
import os
import uuid
from urllib.parse import urlparse

import requests
from playwright.async_api import Page, Locator


# 监听 popup 事件，自动关闭
async def on_close_popup(popup_page):
    # 可选：记录日志或做其他处理
    print(f"on_close_popup, closing: {popup_page.url}")
    try:
        await popup_page.close()
    except Exception:
        # 忽略关闭失败（如已关闭）
        pass


# 场景 1：点击 <a download> 或普通下载链接（直接触发），点击后浏览器不跳转页面，直接开始下载
async def download_direct_link(page: Page, locator: Locator, save_dir: str = "./downloads",
                               timeout: float = 30_000):
    listener_added = False
    try:
        # 添加弹窗处理，关闭弹窗
        page.on("popup", on_close_popup)
        listener_added = True
        os.makedirs(save_dir, exist_ok=True)
        async with page.expect_download(timeout=timeout) as download_info:
            # 不要用 page.click(selector)，而用 locator.click()
            # 除非你确定元素是动态插入且 locator 创建过早
            await locator.wait_for(state="attached", timeout=10_000)
            # locator.click() 内部已包含智能等待，通常无需 wait_for
            # await locator.click(timeout=10_000)
            await locator.click()

        download = await download_info.value
        suggested_name = download.suggested_filename()
        if suggested_name:
            filename = suggested_name
        else:
            download_url = download.url()
            filename = os.path.basename(urlparse(download_url).path) or f"{uuid.uuid4().hex}.bin"

        file_path = os.path.join(save_dir, filename)
        await download.save_as(file_path)
        return file_path
    except TimeoutError as te:
        print(f"Download {page.url} did not start within {timeout / 1000:.1f} seconds")
        return None
    except Exception as e:
        print(f"download_direct_link {page} error: {e}")
        return None
    finally:
        # 清理监听器（避免内存泄漏）
        if listener_added:
            page.remove_listener("popup", on_close_popup)


# 场景 2：点击按钮后打开新页面，新页面自动下载或含下载按钮，点击后弹出 _blank 新窗口，自动开始下载，或需再点一次“确认下载”
async def download_via_popup(page: Page, locator: Locator, save_dir: str = "./downloads",
                             timeout: float = 30_000):
    os.makedirs(save_dir, exist_ok=True)
    # 监听新页面
    async with page.expect_popup(timeout=timeout) as popup_info:
        await locator.click()
    popup = await popup_info.value
    try:
        # 方案 A：新页面自动下载
        async with popup.expect_download(timeout=10000) as download_info:
            await popup.wait_for_load_state("domcontentloaded")
            # 方案 B：新页面需二次点击（取消上面，启用下面）
            # await popup.locator("#download-btn").click()
        download = await download_info.value

        suggested_name = download.suggested_filename()
        if suggested_name:
            filename = suggested_name
        else:
            download_url = download.url()
            filename = os.path.basename(urlparse(download_url).path) or f"{uuid.uuid4().hex}.bin"

        file_path = os.path.join(save_dir, filename)
        await download.save_as(file_path)
        return file_path
    except TimeoutError:
        print(f"Popup opened but no download triggered: {popup.url}")
    finally:
        # 步骤 5: 确保关闭 popup，释放资源
        try:
            await popup.close()
        except Exception:
            # 如果 popup 已关闭（如自动关闭），忽略异常
            pass


# 场景 3：点击后弹出网页内对话框（非系统级），需选择格式/确认

def _is_cookie_domain_match(cookie_domain: str, url_netloc: str) -> bool:
    """
    判断 cookie 的 domain 是否适用于给定 URL 的 netloc。
    例如：
      cookie_domain = ".example.com" → 匹配 "www.example.com", "api.example.com"
      cookie_domain = "example.com"   → 仅匹配 "example.com"
    """
    cookie_domain = cookie_domain.lstrip(".")  # 移除前导点（.example.com → example.com）
    if url_netloc == cookie_domain:
        return True
    # 支持子域名：如果 cookie_domain 是 example.com，则 www.example.com 应匹配
    if url_netloc.endswith("." + cookie_domain):
        return True
    return False


# 从url解析文件名称
def _get_file_name(url: str, resp) -> str:
    parsed_url = urlparse(url)
    # 确定文件名
    filename = os.path.basename(parsed_url.path)
    if not filename or "." not in filename:
        # 如果路径无有效文件名，从 Content-Disposition 或生成 UUID
        content_disposition = resp.headers.get("content-disposition")
        if content_disposition and "filename=" in content_disposition:
            # 简单解析 filename（不处理 quoted-string 等复杂情况）
            filename = content_disposition.split("filename=")[-1].strip('"')
        else:
            ext = resp.headers.get("content-type", "").split("/")[-1]
            ext = "." + (ext if ext and len(ext) <= 5 else "bin")
            filename = f"{uuid.uuid4().hex}{ext}"
    else:
        filename = f"{uuid.uuid4().hex}.bin"
    return filename


# 场景 4：媒体文件（MP3/图片/PDF）被浏览器预览而非下载
async def download_media_by_requests(page, url: str, save_dir: str = "./media"):
    # 获取当前上下文 cookies
    storage = await page.context.storage_state()
    cookies = {c["name"]: c["value"] for c in storage["cookies"]}
    # 2. 【可选】只保留目标域名相关的 cookies
    target_netloc = urlparse(url).netloc
    filtered_cookies = {}
    for c in storage["cookies"]:
        if _is_cookie_domain_match(c["domain"], target_netloc):
            filtered_cookies[c["name"]] = c["value"]

    # 获取当前页面的 User-Agent
    user_agent = await page.evaluate("() => navigator.userAgent")

    resp = requests.get(url, cookies=filtered_cookies or {}, headers={
        "User-Agent": user_agent}, stream=True)
    resp.raise_for_status()

    filename = os.path.basename(urlparse(url).path) or f"{uuid.uuid4().hex}.bin"
    file_path = os.path.join(save_dir, filename)

    os.makedirs(save_dir, exist_ok=True)
    with open(file_path, "wb") as f:
        for chunk in resp.iter_content(8192):
            f.write(chunk)
    return file_path


# 保存文件，save_path为文件全路径
async def save_bytes(save_path: str, body: bytes):
    if body is None:
        print("⚠️ body不存在，跳过保存。")
        return
    if save_path is None:
        print("⚠️ save_path不存在，跳过保存。")
        return

    # 可选：确保目录存在（同步操作，通常很快）
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    async with aiofiles.open(save_path, "wb") as f:
        await f.write(body)
        print(f"✅ 文件已保存: {save_path}")
