from mydemo.llm.agent.agent import Agent
from pydantic import BaseModel, Field
from typing import Type
from dataclasses import dataclass, asdict

# 1. 定义参数 Schema
@dataclass
class UserInput(BaseModel):
    input: str = Field(description="用户输入")
    inputType: str = Field(description="输入的文件格式")
    type: str = Field(description="输出的文件格式")

class FileAgent(Agent):
    name = "file_agent"
    description = "处理各种文件生成的工具"
    args_schema: Type[BaseModel] = UserInput

    def execute_sync(self, **kwargs) -> str:
        print(kwargs)
