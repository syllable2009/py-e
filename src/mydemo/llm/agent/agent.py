from abc import ABC, abstractmethod
import pkgutil
from dataclasses import dataclass, asdict


@dataclass
class Agent(ABC):
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
    def execute_sync(self, **kwargs) -> str:
        raise NotImplementedError("this agent does not support execute sync")

    # @abstractmethod
    # async def execute_asyn(self, **kwargs) -> str:
    #     raise NotImplementedError("this agent does not support execute async")

# 先导入顶包
import mydemo.llm.agent as agent
import importlib
# 2. 遍历包内所有模块,为什么要放在Agent下面
for importer, modname, ispkg in pkgutil.iter_modules(agent.__path__, agent.__name__ + "."):
    if ispkg:
        continue  # 跳过子包（如需要可递归处理）
    print(f"正在导入模块: {modname}")
    importlib.import_module(modname)