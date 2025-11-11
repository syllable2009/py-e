from enum import Enum
from typing import List

from mydemo.walle.action import Action, MessageAction
from mydemo.walle.agent_context import State
from mydemo.walle.agent_loop import AgentLoop


class AgentManagerStatus(Enum):
    """
    AgentManager状态
    """
    RUNNING = "running"  # 运行中
    PENDING = "pending"  # 等待中
    COMPLETED = "completed"  # 完成
    TERMINATION = "termination"  # 终止
    FAILED = "failed"  # 失败
    WAITING_STOP = "waiting_stop"  # 等待终止


class AgentManager:

    def __init__(self, agent_tools: List[str] = None):
        self.state: State = None
        pass

    async def handle_action(self, action: Action) -> None:
        if self._is_finish_status():
            print(f"当前任务已结束")
            return
        # 效验，判断最大执行次数和深度
        print("执行次数超过最大限制")
        print("执行深度超过最大限制")
        if isinstance(action, MessageAction):
            # 处理用户消息，转换多模态数据，构造langchain的HumanMessage对象
            pass
        # 保存数据和状态

        # 通过父id标记是否规划
        if not self.parent_id:
            pass
        else:
            # 目前：子AM都没有委派的能力，所以先不执行plan了，直接执行自己的agent
            await self._execute_agent()

    async def _plan(self):
        # 如果配置了强制agent，不走planner，直接返回结果
        # if self.state.force_agent:
        #     return self._handle_force_agent(obs)
        agent_loop = AgentLoop(state=self.state, agent_tools=self.get_agent_tools())
        return await agent_loop.loop()

    def _is_finish_status(self) -> bool:
        finish_statuses = [
            AgentManagerStatus.TERMINATION,
            AgentManagerStatus.COMPLETED,
            AgentManagerStatus.FAILED,
            AgentManagerStatus.WAITING_STOP
        ]
        return self.status in finish_statuses

    async def _execute_agent(self):
        try:
            print(f"开始执行agent execute方法：{self.agent_name}")
            # BrowserAgent的execute的方法需要使用RPC调用
            if self.agent_name == "BrowserAgent":
                observation = self.execute_browser_agent()
                # observation = AgentCompleteObservation(self.id, "需要用户登录", self.state,
                #                             self.conversation_id, need_human_help=True)
            else:
                # 根据agent的名字获取对应的agent对象
                agent_instance = Agent.get_agent_instance(self.agent_name, self.state)
                observation = await agent_instance.execute(self.state)
                # observation = AgentCompleteObservation(self.id, "执行失败", self.state,
                #                             self.conversation_id, need_human_help=False)

            print(
                f"执行agent execute方法，{self.agent_name} ，返回的observation: {JsonUtils.to_json(observation.content)[:500]}")
            return observation
        except Exception as e:
            print(f"执行agent execute方法出错", e)
            return AgentCompleteObservation(self.id, f"执行{self.agent_name}出错", self.state,
                                            self.conversation_id)
