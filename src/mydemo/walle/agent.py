from abc import ABC, abstractmethod
from typing import Any


class Agent(ABC):

    @abstractmethod
    def get_prompt(self, param: dict = None) -> str:
        pass

    @abstractmethod
    def execute(self, *args: Any, **kwargs: Any) -> Any:
        """
        执行 Agent 的核心逻辑。
        子类必须实现此方法。
        参数和返回值类型可根据具体场景自定义。
        """
        pass


class PlanAgent(Agent):
    pass