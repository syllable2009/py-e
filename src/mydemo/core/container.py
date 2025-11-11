import punq

# 注册服务（顺序无关，punq 支持自动依赖解析）
from mydemo.service.email_service import EmailService
from mydemo.service.user_service import UserService

# 创建全局容器实例
container = punq.Container()

container.register(EmailService)
container.register(UserService)


# 在其他模块中使用
from container import container
class UserHandler:
    def __init__(self):
        # 从容器解析依赖
        user_service1 = container.resolve(UserService)
        print(user_service1)
        print(type(user_service1))





