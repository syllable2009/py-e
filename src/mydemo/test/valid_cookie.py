import asyncio
import datetime

from mydemo.utils.http_util import http_get
# 10:24 创建 11：31 ok 11:41失败，会话结束
jwt = ""

async def main():
    while True:
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"\n🔄 开始检查... (当前时间: {current_time})")
        headers = {
            "Authorization": f"Bearer {jwt}"
        }
        resp = await http_get("https://studio-api.prod.suno.com/api/project/default", headers=headers)
        print(f"Status:{resp.status_code},Response:{resp.json()}")
        # 等待 10 分钟（600 秒）
        await asyncio.sleep(600)

if __name__ == "__main__":
    asyncio.run(main())