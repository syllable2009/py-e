import os
import time
from pathlib import Path

from playwright.async_api import Page


# 截图保存
async def save_screenshot_on_page(
        page: Page,
        screenshot_dir: str = "./screenshots",
        prefix='screenshot'
) -> None:
    Path(screenshot_dir).mkdir(parents=True, exist_ok=True)
    timestamp = int(time.time())
    screenshot_path = os.path.join(screenshot_dir, f"{prefix}_{timestamp}.png")
    try:
        await page.screenshot(path=screenshot_path, full_page=True)
        print(f"已保存截图 {page.url}:{screenshot_path}")
    except Exception as e:
        print(f"在页面 {page.url} 上截图发生错误: {e}")
