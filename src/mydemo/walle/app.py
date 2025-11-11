from mydemo.walle.action import Action, TaskAction, ObservationAction, MessageAction

plan_steps: list = []


def _handle_first_execution():
    # query改写，优化多轮对话关联性差的问题
    #  关联历史会话
    # 判断是否为简单任务
    # 如果是简单问题，直接返回
    # 创建taskAction
    _execute_loop(None)
    pass


def _execute_loop(action: Action):
    # 设置循环结束条件
    if isinstance(action, TaskAction):
        # 思考规划
        _plan()
        for step in plan_steps:
            _execute_loop()
            pass
    elif isinstance(action, MessageAction):
        # 执行
        pass
    elif isinstance(action, ObservationAction):
        pass
    else:
        pass



def _plan():
    # 判断是否已经制定计划

    pass

if __name__ == "__main__":
    pass