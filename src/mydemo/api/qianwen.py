import os
from openai import OpenAI

#Linux/macOS： export API_KEY="sk-xxxxxxxxxxxxxxxx"
#window: set API_KEY=sk-xxxxxxxxxxxxxxxx

client = OpenAI(
    api_key=os.getenv("API_KEY"),
    # 以下是北京地域base_url，如果使用新加坡地域的模型，需要将base_url替换为：https://dashscope-intl.aliyuncs.com/compatible-mode/v1
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
)

messages = [{"role": "user", "content": "你是谁"}]


def chat():
    completion = client.chat.completions.create(
        model="qwen-plus",
        messages=messages
    )
    print(completion.choices[0].message.content)


def chat_with_stream():
    completion = client.chat.completions.create(
        model="qwen-plus-2025-07-28",  # 您可以按需更换为其它深度思考模型
        messages=messages,
        extra_body={"enable_thinking": True},
        stream=True
    )
    is_answering = False  # 是否进入回复阶段
    print("\n" + "=" * 20 + "思考过程" + "=" * 20)
    for chunk in completion:
        delta = chunk.choices[0].delta
        if hasattr(delta, "reasoning_content") and delta.reasoning_content is not None:
            if not is_answering:
                print(delta.reasoning_content, end="", flush=True)
        if hasattr(delta, "content") and delta.content:
            if not is_answering:
                print("\n" + "=" * 20 + "完整回复" + "=" * 20)
                is_answering = True
            print(delta.content, end="", flush=True)


if __name__ == "__main__":
    chat_with_stream()
