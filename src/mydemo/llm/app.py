from pydantic import BaseModel
from typing import Any, Dict, List, get_origin, get_args
from mydemo.llm.tool import AgentTool
from mydemo.llm.tool_impl import WeatherTool, EmailTool
import os
import json
from string import Template

system_prompt = Template('''你是任务规划助手和任务执行监督员，当规划plan为空时，可按用户输入规划任务（用提供的工具组合达成目标），制定规划plan后，负责验证已完成子任务、控制质量。能审查任务流最新执行结果，判断是否符合分配任务及成功标准，为下游代理提供指导与行动建议。具备管理多代理协作、识别任务优先级、保持目标一致及输出明确判断和建议的能力。

可用工具：
$tool_descs
  
技能：
- 检测用户需求主语言，满足显式要求，用60%实质词门槛。
- action为上述工具，拆分为可执行、可衡量步骤，聚焦核心行动。
- action_input为字典，键与工具参数一致。
- 为用户高效制定、管理和优化任务计划。能理解复杂需求，分析成员能力，生成可执行方案。可追踪进度、动态调整，擅长多语言任务分析。
- 审查规划plan任务流中的最新执行结果，判断是否符合任务及标准，跟踪事件流，更新步骤状态。
- 针对验证结果，为下游代理成员提供可执行的后续行动建议，按需重规划未完成步骤，包括继续推进、补充信息、修正错误或变更执行策略等。确保单步“进行中”，完成后推进下一步。仅监督观察，不自主执行任务。
- 如果实在无法规划出合适计划，不要直接回复，执行工具default_agent的结果。

响应规则（输出合法JSON）：
- 返回含plan、next、result字段的json对象。plan是步骤工具列表，next是下一步工具，result是上步结果。
- 工具返回格式：[{"thought":"...","agent":"工具名","state":"状态","action_input":{}}]
- 完成任务时，result为最终结果。

限制：
- 无验证、确认或说明步骤。
- 每次输出含所有任务计划和流程状态。
- 依赖团队协作，不凭内部知识处理任务。''')

# 模拟调用大模型
# client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))  # 请设置环境变量
client = None;


def call_llm(messages, model="gpt-4o"):
    try:
        # response = client.chat.completions.create(
        #     model=model,
        #     messages=messages,
        #     temperature=0.0,
        #     response_format={"type": "json_object"}  # 强制输出 JSON
        # )
        response = """{
  "thought": "我需要先查天气，再发邮件",
  "agent": "get_weather",
  "action_input": {"location": "Beijing"}
}"""
        return json.loads(response)
        # return json.loads(response.choices[0].message.content)
    except Exception as e:
        return {"error": str(e)}


def build_system_prompt(tools: list) -> str:
    if len(tools) == 0:
        tool_descs = {}
    else:
        tool_descs = "\n".join([f"- {t['name']}: {t['description']}, parameters:{t['parameters']}" for t in tools])
    return system_prompt.substitute(tool_descs=tool_descs)


def run_agent(goal: str, tools: list[AgentTool], max_steps: int = 5) -> str:
    # 工具名称映射
    tool_map = {t.name: t for t in tools}

    # 初始化对话历史
    messages = [
        {"role": "system", "content": build_system_prompt(tools)},
        {"role": "user", "content": goal}
    ]
    tool_descs = "\n".join([f"- {t.name}: {t.description}" for t in tools])
    print(f"tool_descs:{tool_descs}")
    print(f"🎯 目标: {goal}\n")

    for step in range(max_steps):
        # 调用 LLM 获取下一步
        response = call_llm(messages)

        if "error" in response:
            return f"LLM 调用错误: {response['error']}"

        # 检查是否最终回答
        if "final_answer" in response:
            print(f"✅ 最终答案: {response['final_answer']}")
            return response["final_answer"]

        # 否则应为 agent
        thought = response.get("thought", "")
        action = response.get("agent")
        action_input = response.get("action_input", {})

        print(f"🧠 Thought: {thought}")
        print(f"🛠️  Action: {action}({action_input})")

        # 执行工具
        if action in tool_map:
            try:
                observation = tool_map[action].execute(**action_input)
            except Exception as e:
                observation = f"执行错误: {str(e)}"
        else:
            observation = f"未知工具: {action}"

        print(f"🔍 Observation: {observation}\n")

        # 将结果加入对话历史后，模型会自动更新节点状态
        messages.append({
            "role": "assistant",
            "content": json.dumps(response, ensure_ascii=False)
        })
        messages.append({
            "role": "user",
            "content": f"Observation: {observation}"
        })

    return "❌ 任务超时，未能完成。"


def _get_type_name(annotation: Any) -> str:
    """将类型注解转换为可读的字符串表示，如 str, int, List[str], Dict[str, int] 等"""
    if annotation is None:
        return "None"

    # 处理泛型（如 List[str], Dict[str, int]）
    origin = get_origin(annotation)
    args = get_args(annotation)

    if origin is not None:
        origin_name = getattr(origin, '__name__', str(origin))
        if args:
            arg_names = ", ".join(_get_type_name(arg) for arg in args)
            return f"{origin_name}[{arg_names}]"
        else:
            return origin_name

    # 普通类型（如 str, int）
    if hasattr(annotation, '__name__'):
        return annotation.__name__
    else:
        return str(annotation).replace("typing.", "")


def get_field_descriptions(cls):
    """
    返回一个字典，key 为 '字段名: 类型'，value 为 Field 的 description。
    示例: {"input: str": "用户输入", ...}
    """
    # 获取工具名称和描述（支持类属性或实例方法）
    name = getattr(cls, 'name', cls.__name__)
    description = getattr(cls, 'description', "")
    result = {
        "name": name,
        "description": description,
        "parameters": []
    }
    # 尝试获取参数 schema
    schema_class = getattr(cls, 'args_schema', None)
    if schema_class and isinstance(schema_class, type) and issubclass(schema_class, BaseModel):
        for field_name, field_info in schema_class.model_fields.items():
            type_str = _get_type_name(field_info.annotation)
            desc = field_info.description or ""
            result["parameters"].append(f"{field_name}({type_str}): {desc}")

    return result


if __name__ == "__main__":

    from mydemo.llm.agent.agent import Agent

    tools = []
    for cls in Agent.__subclasses__():
        tools.append(get_field_descriptions(cls))
        # try:
        #     instance = cls()  # 假设无参构造
        #     tools.append(instance)
        #     print(f"✅ 已加载工具: {cls.__name__}")
        # except Exception as e:
        #     print(f"❌ 无法实例化 {cls.__name__}: {e}")
    # print(tools)
    # # 1. 实例化工具
    print(build_system_prompt(tools))

    # goal = "帮我查北京的天气，并把结果通过邮件发送给 user@example.com"
    # result = run_agent(goal, tools)
    # print(f"result: {result}")
