from typing import List, Dict, Any, Optional
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.tools import Tool
from langchain_openai import ChatOpenAI
from langchain.agents import create_react_agent, AgentExecutor
import re
import math


# ======================
# 1. 自定义工具（可扩展）
# ======================

def search_tool(query: str) -> str:
    """模拟搜索引擎（实际项目中替换为真实 API）"""
    # 示例：硬编码知识库（生产环境应调用 Tavily/DuckDuckGo/内部 DB）
    knowledge = {
        "爱因斯坦出生年份": "阿尔伯特·爱因斯坦出生于1879年。",
        "法国总统 2025": "截至2025年，法国总统是埃马纽埃尔·马克龙。",
        "圆周率": "3.1415926535"
    }
    for k, v in knowledge.items():
        if k in query or query in k:
            return v
    return f"未找到关于 '{query}' 的信息。"


def calculator(expression: str) -> str:
    """安全计算器（仅支持基本数学表达式）"""
    try:
        # 仅允许数字、括号、+ - * / . 和空格
        if not re.match(r'^[\d+\-*/().\s]+$', expression):
            return "错误：表达式包含非法字符"
        # 使用 eval 需谨慎！生产环境建议用 ast.parse 或专用库
        result = eval(expression, {"__builtins__": {}}, {"math": math})
        return str(result)
    except Exception as e:
        return f"计算错误: {str(e)}"


# 注册工具
tools = [
    Tool(
        name="Search",
        func=search_tool,
        description="用于查找事实性信息，如人物、事件、日期等。输入应为简洁的关键词或问题。"
    ),
    Tool(
        name="Calculator",
        func=calculator,
        description="用于执行数学计算。输入应为合法的数学表达式，如 '2 + 3 * 4' 或 'sqrt(16)'。"
    )
]

# ======================
# 2. 手动定义 ReAct Prompt（离线版）
# ======================

react_prompt = ChatPromptTemplate.from_template(
    """Answer the following questions as best you can. You have access to the following tools:

{tools}

Use the following format:

Question: the input question you must answer
Thought: you should always think about what to do
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer
Final Answer: the final answer to the original input question

Begin!

Question: {input}
Thought: {agent_scratchpad}"""
)

# ======================
# 3. 初始化 LLM 和 Agent
# ======================

# 替换为你自己的 API Key 或使用本地模型
llm = ChatOpenJava(model="gpt-4o-mini", temperature=0)

agent = create_react_agent(
    llm=llm,
    tools=tools,
    prompt=react_prompt
)

# 创建执行器（带安全限制）
agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    verbose=True,  # 打印推理过程
    max_iterations=10,  # 最多 10 步，防止死循环
    handle_parsing_errors=True  # 自动处理格式错误
)

# ======================
# 4. 运行示例
# ======================

if __name__ == "__main__":
    questions = [
        "爱因斯坦活了多少岁？",
        "2025年法国总统是谁？",
        "计算 (1879 + 76) 是多少？"
    ]

    for q in questions:
        print(f"\n{'=' * 50}")
        print(f"问题: {q}")
        print(f"{'=' * 50}")
        try:
            result = agent_executor.invoke({"input": q})
            print(f"\n✅ 最终答案: {result['output']}")
        except Exception as e:
            print(f"❌ 执行出错: {e}")