from datetime import datetime

from mydemo.walle.content import MultimodalContent


class Action:
    sender_id: str
    task: str
    multimodal_task: list[MultimodalContent]
    conversation_id: str
    _create_time: datetime
    _env: str


class TaskAction(Action):

    def __init__(self, sender_id: str, task: str,
                 conversation_id: str,
                 multimodal_task: list[MultimodalContent] = []
                 ):
        super().__init__(sender_id, task, multimodal_task, conversation_id)


class MessageAction(Action):
    """
    用户任务
    """
    root_am_id: str
    user_id: int

    def __init__(self, sender_id: str,
                 task: str,
                 conversation_id: str,
                 root_am_id:str,
                 multimodal_task: list[MultimodalContent] = [],
                 user_id: int = None):
        super().__init__(sender_id, task, multimodal_task, conversation_id)
        self.root_am_id = root_am_id
        self.user_id = user_id


class ObservationAction(Action):
    pass