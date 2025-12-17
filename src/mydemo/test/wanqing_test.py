import os
from pathlib import Path

from openai import OpenAI
from dotenv import load_dotenv

# 自动在当前 .py 文件所在目录找 .env
dotenv_path = Path(__file__).parent / ".env"
if dotenv_path.exists():
    load_dotenv(dotenv_path)

# 请确保您已将 API Key 存储在环境变量 WQ_API_KEY 中
# 初始化 OpenAI 客户端，从环境变量中读取您的 API Key
client = OpenAI(
    # 此为默认路径，您可根据业务所在地域进行配置
    base_url="https://wanqing.streamlakeapi.com/api/gateway/v1/endpoints",
    # 从环境变量中获取您的 API Key
    api_key=os.environ.get("WQ_API_KEY")
)

print("----- streaming request -----")
stream = client.chat.completions.create(
    model="kat-coder-pro-v1",  # kat-coder-pro-v1 为您当前的智能体应用的ID
    messages=[
        {"role": "system", "content": "你是一个 AI 人工智能助手"},
        {"role": "user", "content": "请用java实现一个动态配置类"},
    ],
    stream=True,
)
for chunk in stream:
    if not chunk.choices:
        continue
    if chunk.choices[0].delta.content:
        print(chunk.choices[0].delta.content, end="")

