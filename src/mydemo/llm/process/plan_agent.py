from mydemo.llm.agent.agent import Agent
from pydantic import BaseModel, Field
from typing import Type
from dataclasses import dataclass, asdict
from string import Template

from mydemo.llm.app import get_field_descriptions

### 执行目标规划

system_prompt = Template('''你是任务规划助手，判断用户的问题是属于简单问题还是复杂问题，当为复杂问题时，可按用户输入规划任务（用提供的工具组合达成目标），制定规划plan。

可用工具：
$tool_descs
  
技能：
- 检测用户需求主语言，满足显式要求，用60%实质词门槛。
- action为上述工具，拆分为可执行、可衡量步骤，聚焦核心行动。
- action的输入参数为字典，键与工具参数一致。
- 为用户高效制定、管理和优化任务计划。能理解复杂需求，分析成员能力，生成可执行方案。可追踪进度、动态调整，擅长多语言任务分析。
- 如果实在无法规划出合适计划，不要直接回复，执行工具default_agent的结果。

响应规则（输出合法JSON）：
- 返回含plan、next、result、task字段的json对象。plan是步骤工具列表，next是下一步工具，result是最新工具的结果，task是判断问题类型是简单('simple')还是复杂('complex')的字符串。
- 工具返回格式：[{"thought":"...","agent":"工具名","state":"状态","action_input":{}, "task":"..."}]
- 完成任务时，result为最终结果。

限制：
- 无验证、确认或说明步骤。
- 每次输出含所有任务计划和流程状态。
- 依赖团队协作，不凭内部知识处理任务。''')

# 1. 定义参数 Schema
@dataclass
class UserInput(BaseModel):
    input: str = Field(description="用户输入")

class PlanAgent():
    name = "plan_agent"
    description = "自动规划用户的请求"
    args_schema: Type[BaseModel] = UserInput

    def execute_sync(self, **kwargs) -> str:
        print(kwargs)

def build_system_prompt(tools: list) -> str:
    if len(tools) == 0:
        tool_descs = {}
    else:
        tool_descs = "\n".join([f"- {t['name']}: {t['description']}, parameters:{t['parameters']}" for t in tools])
    return system_prompt.substitute(tool_descs=tool_descs)

if __name__ == "__main__":

    from mydemo.llm.agent.agent import Agent

    tools = []
    for cls in Agent.__subclasses__():
        tools.append(get_field_descriptions(cls))
    # # 1. 实例化工具
    print(build_system_prompt(tools))