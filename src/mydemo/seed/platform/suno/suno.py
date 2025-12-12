import asyncio
import json
from playwright.async_api import async_playwright, expect
from mydemo.seed.service import AbstractCrawler
from mydemo.utils.http_util import http_get
from mydemo.utils.page_util import get_locate_by_xpath

TARGET_URL = "auth.suno.com/v1/client"
# 10:24 创建
jwt = ""

def log_request(request):
    if TARGET_URL in request.url:
        print("\n🔍 捕获到目标请求:")
        print(f"  URL: {request.url}")
        print(f"  Method: {request.method}")
        print(f"  Headers: {json.dumps(request.headers, indent=2, ensure_ascii=False)}")

        # 尝试获取 POST/PUT 请求体（仅限已发送的请求）
        try:
            post_data = request.post_data
            if post_data:
                print(f"  Body: {post_data}")
            else:
                print("  Body: (无)")
        except Exception as e:
            print(f"  ❌ 获取请求体失败: {e}")


def handle_response(response):
    # 获取响应 URL 和 headers
    url = response.url
    headers = response.headers  # dict 类型
    print(f"url:{url},headers:{headers}")
    # 假设 JWT 在 Authorization 头中（常见于 Bearer Token）
    auth_header = headers.get("authorization")  # 注意：Playwright 返回的 header key 是小写的！

    # 或者 JWT 在自定义头中，比如 "x-auth-token"
    jwt_token = headers.get("x-auth-token")

    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.split(" ")[1]
        print(f"✅ 捕获到 JWT Token: {token}")
    elif jwt_token:
        print(f"✅ 捕获到自定义 JWT: {jwt_token}")


async def log_response(response):
    if TARGET_URL in response.url:
        print("\n✅ 捕获到目标响应:")
        print(f"  URL: {response.url}")
        print(f"  Status: {response.status}")
        print(f"  Headers: {json.dumps(response.headers, indent=2, ensure_ascii=False)}")

        # 尝试读取响应体（注意：必须在响应完成前读取）
        try:
            body = await response.body()
            if body:
                # 尝试解析为 JSON
                try:
                    json_body = json.loads(body.decode('utf-8'))
                    print(f"  Body (JSON): {json.dumps(json_body, indent=2, ensure_ascii=False)}")
                    jwt = json_body["response"]["sessions"][0]["last_active_token"]["jwt"]
                    print(f"jwt:{jwt}")
                except UnicodeDecodeError:
                    print(f"  Body (Binary): {body[:100]}...")  # 截断显示
                except json.JSONDecodeError:
                    print(f"  Body (Text): {body.decode('utf-8', errors='replace')}")
            else:
                print("  Body: (空)")
        except Exception as e:
            print(f"  ❌ 获取响应体失败: {e}")


class SunoCrawler(AbstractCrawler):

    def __init__(self) -> None:
        super().__init__()
        self.index_url = "https://suno.com/"

    async def load_with_playwright(self):
        with open("auth.json") as f:
            auth = json.load(f)
        await self.browser_context.add_cookies(auth["cookies"])

    async def do_with_playwright(self) -> None:
        # await self.load_with_playwright()
        self.context_page = await self.browser_context.new_page()
        # cookies = await self.browser_context.cookies()
        # 方法 1：获取 suno.com 及其子域的所有 Cookie
        # cookies = await self.context.cookies("https://suno.com")

        # 注册响应监听器
        self.context_page.on("request", log_request)
        self.context_page.on("response", log_response)
        await self.context_page.goto(self.index_url, wait_until="domcontentloaded", timeout=10000)
        await asyncio.sleep(3)
        # localStorage 是 origin（协议 + 域名 + 端口）隔离的
        # local_storage = await self.context_page.evaluate("() => JSON.stringify(localStorage)")
        # with open("auth.json", "w") as f:
        #     json.dump({
        #         "cookies": cookies,
        #         "local_storage": local_storage
        #     }, f, indent=2)
        # 判断登录信息，已经登录了
        # 获取当前用户信息
        # 构造 headers

        headers = {
            "Authorization": f"Bearer {jwt}"
        }
        resp = await http_get("https://studio-api.prod.suno.com/api/session/", headers=headers)
        print(f"resp:{resp.json()}")
        create_btn = '/html/body/div[1]/div[1]/div[1]/div[3]/a[2]/span/span'

        await get_locate_by_xpath(self.context_page, create_btn, state="attached")

        # await self.choose_model()
        # await self.add_lyrics()
        # 创建音乐
        # await self.create_music()
        await asyncio.sleep(3)

        if 1 == 1:
            return
        # 模拟浏览器操作
        resp = await http_get("https://studio-api.prod.suno.com/api/project/default", headers=headers)
        print(f"resp2:{resp.json()}")
        # 定位到创作页面
        print(f"定位到创作页面")
        await self.context_page.locator('xpath=/html/body/div[1]/div[1]/div[1]/div[3]/a[2]/span/span').click()
        await asyncio.sleep(3)
        # 定位输入框
        print(f"定位输入框")
        xpath = '//*[@id="main-container"]/div/div/div/div/div/div[3]/div/div[2]/div[3]/div/div/div[2]/div/div[1]/div[1]/div/textarea'

        await self.context_page.locator(f'xpath={xpath}').fill('get the moon')
        await asyncio.sleep(3)

        # 定位到创建元素的按钮
        xpath = '//*[@id="main-container"]/div/div/div/div/div/div[3]/div/div[3]/button[2]/span'
        await expect(self.context_page.locator(xpath)).to_be_visible(timeout=10_000)
        print(f"发现创建按钮可用")
        await asyncio.sleep(3)

    async def get_session(self):
        url = "https://studio-api.prod.suno.com/api/session/"

    async def choose_model(self):
        await self.context_page.goto("https://suno.com/create", wait_until="domcontentloaded", timeout=10000)
        xpath = '//*[@id="main-container"]/div/div/div/div/div/div[3]/div/div[1]/div[3]/div/button/span'
        await self.context_page.locator(f"xpath={xpath}").click()
        await asyncio.sleep(3)
        xpath = '/html/body/div[11]/div/div/div[5]/button/span'
        await self.context_page.locator(f'xpath={xpath}').click()
        await asyncio.sleep(3)

    async def add_lyrics(self):
        await self.context_page.goto("https://suno.com/create", wait_until="domcontentloaded", timeout=10000)
        await asyncio.sleep(3)
        xpath = '//*[@id="main-container"]/div/div/div/div/div/div[3]/div/div[2]/div[2]/div[2]/div/div[2]/div/div[1]/div[1]/div/textarea'
        await self.context_page.locator(f'xpath={xpath}').fill("你好夜晚")
        await asyncio.sleep(3)


    # https://studio-api.prod.suno.com/api/project/default
    # https://studio-api.prod.suno.com/api/feed/v3
    async def get_music_list(self):
        pass

    async def create_music(self):
        xpath = '//*[@id="main-container"]/div/div/div/div/div/div[3]/div/div[3]/button[2]'
        self.context_page.locator(f"xpath={xpath}").click()
        await asyncio.sleep(3)


