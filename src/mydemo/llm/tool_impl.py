from mydemo.llm.tool import AgentTool
from pydantic import BaseModel, Field

# 1. 定义参数 Schema
class EmailInput(BaseModel):
    to: str = Field(description="收件人邮箱地址，例如 'user@example.com'")
    subject: str = Field(description="邮件主题，简明扼要")
    body: str = Field(description="邮件正文内容，可包含多行文本")

class WeatherTool(AgentTool):
    name = "get_weather"
    description = "获取指定城市的当前天气。参数: location (str)"

    def execute(self, location: str) -> str:
        # 模拟 API 调用
        return f"Weather in {location}: Sunny, 25°C"

class EmailTool(AgentTool):
    name = "send_email"
    description = "发送一封邮件。参数: to (str), subject (str), body (str)"
    args_schema = EmailInput

    def execute(self, to: str, subject: str, body: str) -> str:
        return f"✅ Email sent to {to} | Subject: {subject} | Body: {body[:30]}..."

class UnSupportTool(AgentTool):
    name = "un_support"
    description = "默认工具,无法匹配到合适的工具时选择此工具"