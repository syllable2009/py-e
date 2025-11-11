### agent的上下文对象，类似state
from dataclasses import field


class AgentContext:
    def __init__(self, agent_name: str) -> None:
        self.agent_name = agent_name


class State:
    # 目标任务
    # 全局迭代次数
    global_iteration: int = 0
    # 局部迭代次数
    local_iteration: int = 0
    # 最大迭代次数
    max_iterations: int = 12
    # 当前迭代层数
    delegate_level: int = 0

    # 回调的kafka topic
    callback_topic: str = None
    # 指定agent配置（配置见 OpenApiChatAPI 注解）
    agent_configs: list[dict] = field(default_factory=list)
    # 强制使用指定agent
    force_agent: str = None

    # 任务规划列表
    plan_steps_md: str = None
    # 任务规划对象
    plan_steps: list[dict] = field(default_factory=list)

    def __init__(self, agent_name: str) -> None:
        self.agent_name = agent_name
