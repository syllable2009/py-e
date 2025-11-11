from typing import Optional, List

from mydemo.walle.agent_context import State


# 根据agent名称返回模型对象，动态配置
def get_agent_llm_model(agent_name: str) -> None:
    return None


class AgentLoopResult:
    pass


class Supervisor:
    pass


class AgentLoop:

    def __init__(self, state: Optional[State] = None, agent_tools: List[str] = None):
        self.model = get_agent_llm_model("AgentLoop")

    async def loop(self) -> AgentLoopResult:

        query_ = await self.rewrite_query()
        # 如果是首次执行，进行处理
        if not self.state.plan_steps_md:
            result = await self._handle_first_execution()
            if result:  # 简单问题直接返回结果
                return result
        return await self._execute_loop()

    # # query改写，优化多轮对话关联性差的问题
    #  关联历史会话
    async def rewrite_query(self, query: str) -> str:
        return query

    async def _handle_first_execution(self) -> Optional[AgentLoopResult]:
        # 判断是否是简单任务
        pass

    async def _execute_loop(self) -> AgentLoopResult:
        """
        执行主要的循环逻辑

        Returns:
            AgentLoopResult: 执行结果
        """
        latest_agent_name = self._get_latest_agent_name()
        need_reflect = latest_agent_name not in {"Planner", "AgentLoopSupervisor", "Supervisor"}

        if need_reflect:
            return await self._handle_reflection()
        else:
            return await self._handle_normal_execution()

    # 处理思考
    async def _handle_reflection(self) -> AgentLoopResult:
        """
              处理反思逻辑

              Args:
                  messages: 消息列表

              Returns:
                  AgentLoopResult: 执行结果
            """
        reflection = await Supervisor(self.state, self.agent_tools).reflection()
        # 发消息
        # 更新状态
        # 保存反思上下文
        # 根据反思结果决定下一步
        if reflection.passed:
            await self._plan_with_message()
        return await self._execute_loop()

    async def _handle_normal_execution(self) -> AgentLoopResult:
        # 正常大模型调用执行结果
        loop_result = None
        return await self._process_loop_result(loop_result)

    async def _plan_with_message(self) -> AgentLoopResult:
        """
                执行规划并发送相关消息事件

                Args:
                    step: 执行步骤

                Returns:
                    PlannerResult: 规划结果
        """
        # plan_agent = PlanAgent(self.state, self.agent_tools, self.channel_name)
        # todo_step_plan = await plan_agent.plan(plan_target)
        # if not task_end:  # 不是发送最终状态，则发送规划响应消息
        pass

    def _get_latest_agent_name(self) -> Optional[str]:
        """获取最新消息的代理名称"""
        if not self.state.messages:
            return None

        latest_message = self.state.messages[-1]
        if isinstance(latest_message, dict):
            return latest_message.get("name")
        return getattr(latest_message, "name", None)
