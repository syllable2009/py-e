from abc import ABC, abstractmethod
from typing import Dict, Any

class AgentTool(ABC):
    """所有工具必须继承此类，并实现 execute 和提供 description"""

    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        pass

    @abstractmethod
    def execute(self, **kwargs) -> str:
        pass