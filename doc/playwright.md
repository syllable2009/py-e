# 安装包和浏览器二进制程序
pip install --no-cache-dir --index-url https://pypi.tuna.tsinghua.edu.cn/simple playwright
python -m playwright install chromium




# 在 Playwright 中，触发文件下载有多种常见场景
# 场景 1：点击 <a download> 或普通下载链接（直接触发），点击后浏览器不跳转页面，直接开始下载
最佳实践：使用 expect_download() + locator.click()
async def download_direct_link(page, selector: str, save_dir: str = "./downloads"):
    os.makedirs(save_dir, exist_ok=True)
    
    async with page.expect_download() as download_info:
        # 不要用 page.click(selector)，而用 locator.click()
        await page.locator(selector).click()
    
    download = await download_info.value
    file_path = os.path.join(save_dir, await download.suggested_filename())
    await download.save_as(file_path)
    return file_path
# 场景 2：点击按钮后打开新页面，新页面自动下载或含下载按钮，点击后弹出 _blank 新窗口，自动开始下载，或需再点一次“确认下载”
最佳实践：监听 popup + 在新页面中处理下载
async def download_via_popup(page, trigger_selector: str, save_dir: str = "./downloads"):
    os.makedirs(save_dir, exist_ok=True)
    
    # 监听新页面
    async with page.expect_popup() as popup_info:
        await page.locator(trigger_selector).click()
    
    popup = await popup_info.value
    
    try:
        # 方案 A：新页面自动下载
        async with popup.expect_download(timeout=10000) as dl_info:
            await popup.wait_for_load_state("domcontentloaded")
        download = await dl_info.value
        
        # 方案 B：新页面需二次点击（取消上面，启用下面）
        # async with popup.expect_download() as dl_info:
        #     await popup.locator("#download-btn").click()
        # download = await dl_info.value
        
        file_path = os.path.join(save_dir, await download.suggested_filename())
        await download.save_as(file_path)
        return file_path
        
    finally:
        await popup.close()  # 关闭弹出页，避免资源占用

# 场景 3：点击后弹出网页内对话框（非系统级），需选择格式/确认
最佳实践：操作 DOM 弹窗 + 触发下载
async def download_with_format_choice(page, trigger_selector: str, format_btn: str, confirm_btn: str):
    # 1. 点击触发弹窗
    await page.locator(trigger_selector).click()
    
    # 2. 等待弹窗出现
    await page.wait_for_selector(".download-dialog", state="visible")
    
    # 3. 选择格式（如 PDF）
    await page.locator(format_btn).click()  # e.g., "button.format-pdf"
    
    # 4. 点击确认并捕获下载
    async with page.expect_download() as dl_info:
        await page.locator(confirm_btn).click()  # e.g., ".download-dialog .confirm"
    
    download = await dl_info.value
    await download.save_as("./report.pdf")

# 场景 4：媒体文件（MP3/图片/PDF）被浏览器预览而非下载
最佳实践：绕过浏览器，用 HTTP 客户端下载（推荐）
import requests

async def download_media_by_requests(page, url: str, save_dir: str = "./media"):
    # 获取当前上下文 cookies
    storage = await page.context.storage_state()
    cookies = {c["name"]: c["value"] for c in storage["cookies"]}
    # 2. 【可选】只保留目标域名相关的 cookies
    target_netloc = urlparse(url).netloc
    filtered_cookies = {}
    for c in storage["cookies"]:
        if target_netloc.endswith(c["domain"].lstrip(".")):
            filtered_cookies[c["name"]] = c["value"]    

    resp = requests.get(url, cookies=cookies=filtered_cookies or cookies, headers={"User-Agent": "Mozilla/5.0"}, stream=True)
    resp.raise_for_status()
    
    filename = os.path.basename(urlparse(url).path) or "media.bin"
    file_path = os.path.join(save_dir, filename)
    
    os.makedirs(save_dir, exist_ok=True)
    with open(file_path, "wb") as f:
        for chunk in resp.iter_content(8192):
            f.write(chunk)
    return file_path
替代方案（高级）：用 page.route() 强制添加 Content-Disposition: attachment
await page.route("**/*.mp3", lambda route: route.fulfill(
    response=await route.fetch(),
    headers={**route.request.headers, "content-disposition": "attachment"}
))

# 场景 5：通过表单提交（POST）触发下载
最佳实践：直接监听下载（无需特殊处理）
async def download_via_form(page, submit_btn: str):
    async with page.expect_download() as dl_info:
        await page.locator(submit_btn).click()
        # 可加等待：await page.wait_for_selector(".loading", state="hidden")
    
    download = await dl_info.value
    await download.save_as("./export.xlsx")

# locator
page.get_by_role("link", name=re.compile(r"亚⭐️太", re.IGNORECASE)).click()
page.get_by_text("亚⭐️太", exact=False).click()

推荐使用优先级（从高到低）
getByTestId() —— 最稳定，需团队约定
getByRole() / getByLabel() —— 语义化、可访问性友好
getByText() —— 用户视角，直观
CSS 选择器（带稳定 class/id） —— 快速但需谨慎
XPath / 复杂组合 —— 仅作为兜底方案


