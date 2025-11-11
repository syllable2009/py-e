import punq

# 如果 container.py 导入太多模块，可能引发循环导入。
# 解决方案：延迟注册（推荐）
__container = None


def create_container():
    container = punq.Container()

    # 延迟导入，避免顶层导入,使用函数内 import 防止循环导入
    # 注册服务（顺序无关，punq 支持自动依赖解析）
    from mydemo.service.email_service import EmailService
    from mydemo.service.user_service import UserService
    container.register(EmailService)
    container.register(UserService)
    return container


def get_container():
    global _container
    if _container is None:
        # 创建全局容器实例
        _container = create_container()
    return _container


class UserHandler:
    def __init__(self):
        # 从容器解析依赖
        # 在其他模块中使用
        container = get_container()
        # 按需解析调用
        # container.resolve("UserService")  # 或直接传类
        from mydemo.service.user_service import UserService
        user_service1 = container.resolve(UserService)
        print(user_service1)
        print(type(user_service1))
