from mydemo.llm.agent.agent import Agent
from pydantic import BaseModel, Field
from typing import Type
from dataclasses import dataclass, asdict

# 1. 定义参数 Schema
@dataclass
class UserInput(BaseModel):
    input: str = Field(description="用户输入")

class SearchAgent(Agent):
    name = "search_agent"
    description = "联网搜索内容"
    args_schema: Type[BaseModel] = UserInput

    def execute_sync(self, **kwargs) -> str:
        print(kwargs)
