from dataclasses import dataclass
from typing import Optional, Dict, Any, List,Callable
import json
results = {}
# 工具函数示例
def get_weather(location: str) -> str:
    # 模拟 API 调用
    return f"Weather in {location}: Sunny, 25°C"

def send_email(to: str, subject: str, body: str) -> str:
    return f"Email sent to {to} with subject '{subject}'"

# 注册可用工具（实际项目中可动态加载）
TOOLS = {
    "get_weather": get_weather,
    "send_email": send_email,
}

# 工具描述（供 LLM 理解能力）
TOOL_DESCRIPTIONS = {
    "get_weather": "获取指定城市的天气，参数: location (str)",
    "send_email": "发送邮件，参数: to (str), subject (str), body (str)",
}

@dataclass
class Task:
    id: int
    description: str  # 人类可读描述
    tool_name: str  # 要调用的工具名
    args: Dict[str, Any]  # 参数字典
    result: Optional[str] = None
    success: bool = False


def mock_llm_planner(goal: str, feedback: str = "") -> List[Dict]:
    """
    模拟 LLM 返回任务计划。
    实际应调用真实大模型。
    """
    if "weather" in goal.lower():
        plan = [
            {"tool": "get_weather", "args": {"location": "Beijing"}},
            {"tool": "send_email",
             "args": {"to": "user@example.com", "subject": "Weather Report", "body": "{{result_0}}"}}
        ]
    else:
        plan = [{"tool": "get_weather", "args": {"location": "Unknown"}}]

    # 简单模拟失败重规划
    if "retry" in feedback:
        plan[0]["args"]["location"] = "Shanghai"

    return plan


def execute_and_validate_tasks(tasks: List[Task]) -> bool:
    """执行所有任务并验证结果"""
    global results
    for task in tasks:
        try:
            if task.tool_name not in TOOLS:
                task.result = f"Tool '{task.tool_name}' not found"
                task.success = False
                continue

            # 执行工具
            func = TOOLS[task.tool_name]
            task.result = func(**task.args)
            task.success = True

            # 存储结果供后续任务引用（如 {{result_0}}）
            results[f"result_{task.id}"] = task.result

        except Exception as e:
            task.result = f"Error: {str(e)}"
            task.success = False

    # 简单验证：所有任务必须成功
    return all(t.success for t in tasks)

def run_autonomous_agent(goal: str, max_retries: int = 2):
    feedback = ""

    for attempt in range(max_retries + 1):
        print(f"\n🔄 尝试第 {attempt + 1} 次规划...")

        # 1. 规划
        raw_plan = mock_llm_planner(goal, feedback)

        print(f"raw_plan: {raw_plan}")

        # 2. 构建 Task 对象
        tasks = []
        for i, step in enumerate(raw_plan):
            # 替换模板变量（如 {{result_0}}）
            args = {}
            for k, v in step["args"].items():
                if isinstance(v, str) and "{{" in v:
                    key = v.strip("{} ")
                    args[k] = results.get(key, v)  # 若无结果，保留原字符串
                else:
                    args[k] = v
            tasks.append(Task(id=i, description=f"Step {i + 1}", tool_name=step["tool"], args=args))

        # 3. 执行 + 验证
        success = execute_and_validate_tasks(tasks)

        # 4. 打印结果
        print("\n📋 执行结果:")
        for t in tasks:
            status = "✅" if t.success else "❌"
            print(f"{status} {t.description}: {t.result}")

        if success:
            print("\n🎉 所有任务成功完成！")
            return tasks[-1].result if tasks else "No result"
        else:
            feedback = "Previous plan failed. Retry with corrected parameters."
            print(f"\n⚠️ 任务失败，准备重规划...")

    raise RuntimeError("Agent failed after maximum retries")


if __name__ == "__main__":
    goal = "帮我查北京天气，并把结果发邮件给 user@example.com"
    final_result = run_autonomous_agent(goal)
    print(f"\n🎯 最终输出: {final_result}")
