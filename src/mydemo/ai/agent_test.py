from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
import json

# ---------------------------
# 工具接口
# ---------------------------
class Tool(ABC):
    name: str
    description: str

    @abstractmethod
    def __call__(self, input_str: str) -> str:
        pass

# 示例工具：计算器
class Calculator(Tool):
    name = "Calculator"
    description = "Evaluate a mathematical expression. Input should be a valid Python expression."

    def __call__(self, input_str: str) -> str:
        try:
            return str(eval(input_str))
        except Exception as e:
            return f"Error: {e}"

# 示例工具：搜索（模拟）
class SearchTool(Tool):
    name = "Search"
    description = "Search the web for information."

    def __call__(self, query: str) -> str:
        # 模拟返回结果
        return f"Top result for '{query}': The answer is 42."

# ---------------------------
# LLM 接口（简化）
# ---------------------------
class LLM:
    def generate(self, prompt: str) -> str:
        # 实际使用中替换为真实 LLM 调用（如 OpenAI API）
        # 这里用 mock 演示逻辑
        if "Thought:" in prompt and "What is 6 * 7?" in prompt:
            return 'Action: Calculator\nAction Input: "6 * 7"'
        elif "Observation:" in prompt and "42" in prompt:
            return "Thought: Now I know the answer.\nFinal Answer: 42"
        elif "Reflect on why you failed" in prompt:
            return "Reflection: I should have used the calculator earlier instead of guessing."
        else:
            return "Thought: I need to search for more information.\nAction: Search\nAction Input: \"What is the capital of France?\""

# ---------------------------
# Agent 主体
# ---------------------------
class ReActReflexionAgent:
    def __init__(self, llm: LLM, tools: List[Tool], max_steps: int = 10, max_reflections: int = 3):
        self.llm = llm
        self.tools = {tool.name: tool for tool in tools}
        self.max_steps = max_steps
        self.max_reflections = max_reflections

    def run(self, question: str) -> str:
        reflections = []
        for attempt in range(self.max_reflections + 1):
            trajectory = self._react_loop(question, reflections)
            final_answer = self._extract_final_answer(trajectory)
            if final_answer:
                return final_answer
            else:
                reflection = self._reflect(trajectory, question)
                reflections.append(reflection)
                print(f"[Reflection {attempt + 1}] {reflection}")
        return "Failed to solve the task after multiple reflections."

    def _react_loop(self, question: str, past_reflections: List[str]) -> List[Dict[str, str]]:
        trajectory = []
        steps = 0
        prompt = self._build_initial_prompt(question, past_reflections)

        while steps < self.max_steps:
            response = self.llm.generate(prompt).strip()
            thought, action, action_input, final_answer = self._parse_response(response)

            if final_answer:
                trajectory.append({"Thought": thought, "Final Answer": final_answer})
                break

            observation = ""
            if action in self.tools:
                observation = self.tools[action](action_input)
            else:
                observation = f"Error: Unknown action '{action}'"

            step_log = {
                "Thought": thought,
                "Action": action,
                "Action Input": action_input,
                "Observation": observation
            }
            trajectory.append(step_log)
            prompt += f"\n{response}\nObservation: {observation}"
            steps += 1

        return trajectory

    def _build_initial_prompt(self, question: str, reflections: List[str]) -> str:
        tool_descs = "\n".join([f"{t.name}: {t.description}" for t in self.tools.values()])
        refl_text = "\n".join([f"- {r}" for r in reflections])
        prompt = (
            f"Question: {question}\n"
            f"Tools:\n{tool_descs}\n"
        )
        if reflections:
            prompt += f"Previous Reflections:\n{refl_text}\n"
        prompt += "Thought:"
        return prompt

    def _parse_response(self, text: str):
        lines = text.split('\n')
        thought = ""
        action = ""
        action_input = ""
        final_answer = ""

        for line in lines:
            if line.startswith("Thought:"):
                thought = line[len("Thought:"):].strip()
            elif line.startswith("Action:"):
                action = line[len("Action:"):].strip()
            elif line.startswith("Action Input:"):
                action_input = line[len("Action Input:"):].strip().strip('"')
            elif line.startswith("Final Answer:"):
                final_answer = line[len("Final Answer:"):].strip()

        return thought, action, action_input, final_answer

    def _extract_final_answer(self, trajectory: List[Dict]) -> Optional[str]:
        if trajectory and "Final Answer" in trajectory[-1]:
            return trajectory[-1]["Final Answer"]
        return None

    def _reflect(self, trajectory: List[Dict], question: str) -> str:
        traj_str = "\n".join([
            f"Step {i+1}: " + json.dumps(step, indent=2)
            for i, step in enumerate(trajectory)
        ])
        reflect_prompt = (
            f"Question: {question}\n"
            f"Your attempt failed to produce a Final Answer.\n"
            f"Trajectory:\n{traj_str}\n"
            f"Reflect on why you failed. What should you do differently next time?\n"
            f"Reflection:"
        )
        return self.llm.generate(reflect_prompt).strip()

# ---------------------------
# 使用示例
# ---------------------------
if __name__ == "__main__":
    llm = LLM()
    tools = [Calculator(), SearchTool()]
    agent = ReActReflexionAgent(llm, tools)

    question = "What is 6 multiplied by 7?"
    answer = agent.run(question)
    print(f"✅ Final Answer:{answer}")
