from typing import Union, Tuple, Optional


class BusinessException(Exception):
    """业务异常基类
    
    可以通过以下方式创建异常：
    1. 直接传递消息和错误码: BusinessException("错误消息", 500)
    2. 传递BusinessExceptionConstant: BusinessException(BusinessExceptionConstant.RUNNING_CONVERSATION_EXISTS)
    3. 只传递消息: BusinessException("错误消息")
    raise BusinessException(f"AgentLoop执行失败: {str(e)}")
    """
    
    def __init__(self, 
                 message: Union[str, Tuple[int, str]] = '系统异常', 
                 code: Optional[int] = -1):
        """
        初始化业务异常
        
        Args:
            message: 错误消息字符串或BusinessExceptionConstant元组
            code: 错误码（当第一个参数是字符串时使用）
        """
        if isinstance(message, tuple):
            # 如果传入的是BusinessExceptionConstant元组
            error_code, error_message = message
            self.code = error_code
            self.message = error_message
        else:
            # 如果传入的是字符串消息
            self.message = message
            self.code = code
        
        super().__init__(self.message)

    