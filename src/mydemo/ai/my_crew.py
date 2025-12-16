import os

# 🔒 关键：彻底禁用所有可能的网络行为
os.environ["OPENAI_API_KEY"] = "dummy"
os.environ["LANGCHAIN_TRACING_V2"] = "false"
os.environ["LANGCHAIN_ENDPOINT"] = ""
os.environ["LANGCHAIN_API_KEY"] = ""
os.environ["LANGCHAIN_PROJECT"] = ""

# 可选：禁用警告
os.environ["TOKENIZERS_PARALLELISM"] = "false"

from crewai import Agent, Task, Crew
from langchain_community.llms import FakeListLLM

# 🧪 完全离线的 Mock LLM
fake_llm = FakeListLLM(
    responses=[
        "调研结果：2025年主流Python自动化框架有CrewAI（多Agent协作）、LangGraph（状态机工作流）、AutoGen（多Agent对话编程）。",
        "【技术简报】2025年，AI自动化框架快速发展。CrewAI适合任务编排，LangGraph支持复杂流程控制，AutoGen擅长代码生成。三者均为开源项目，社区活跃，是构建可靠智能体的核心工具。",
        "审核通过：内容准确，无虚构信息，字数符合要求。"
    ]
)

# 创建 Agents（最小化配置，避免隐式行为）
researcher = Agent(
    role="技术研究员",
    goal="调研2025年Python AI自动化框架",
    backstory="你是AI系统专家，只基于已有知识回答",
    llm=fake_llm,
    verbose=True,
    allow_delegation=False,
    # 关键：禁用记忆和工具，确保纯本地
    tools=[],
    memory=False,
)

writer = Agent(
    role="技术作家",
    goal="撰写简洁中文简报",
    backstory="你根据给定信息写作，不联网查询",
    llm=fake_llm,
    verbose=True,
    allow_delegation=False,
    tools=[],
    memory=False,
)

reviewer = Agent(
    role="质量审核员",
    goal="验证内容是否准确合规",
    backstory="你仅基于输入内容判断，不引入外部知识",
    llm=fake_llm,
    verbose=True,
    allow_delegation=False,
    tools=[],
    memory=False,
)

# 定义任务
task1 = Task(
    description="列出2025年三个主流Python AI自动化框架及其特点",
    expected_output="包含CrewAI、LangGraph、AutoGen的要点列表",
    agent=researcher,
)

task2 = Task(
    description="基于上述调研，写一段100字左右的中文简报",
    expected_output="一段结构清晰的技术简报",
    agent=writer,
)

task3 = Task(
    description="审核简报是否事实准确、无幻觉、字数合适",
    expected_output="'审核通过' 或具体修改意见",
    agent=reviewer,
)

# 创建 Crew（verbose 必须是 bool！）
crew = Crew(
    agents=[researcher, writer, reviewer],
    tasks=[task1, task2, task3],
    verbose=True,  # ✅ 布尔值，不是 2
    memory=False,  # 全局关闭记忆
)

# 执行（完全离线）
result = crew.kickoff()

print("\n" + "="*50)
print("✅ 最终输出（完全本地模拟，未联网）:")
print("="*50)
print(result)