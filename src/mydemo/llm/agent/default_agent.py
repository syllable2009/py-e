from mydemo.llm.agent.agent import Agent
from pydantic import BaseModel, Field
from typing import Type
from dataclasses import dataclass, asdict

# 1. 定义参数 Schema
@dataclass
class UserInput(BaseModel):
    input: str = Field(description="用户输入")

class DefaultAgent(Agent):
    name = "default_agent"
    description = "兜底的默认工具"
    args_schema: Type[BaseModel] = UserInput

    def execute_sync(self, **kwargs) -> str:
        print(kwargs)
