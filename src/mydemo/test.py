TOOLS = {}

def register_tool(name: str):
    def decorator(func):
        print(f"[装饰器执行] 注册工具: {name}")
        TOOLS[name] = func
        return func
    return decorator

@register_tool("hello")
def say_hello():
    print("[函数执行] Hello!")

print("---- 开始调用 ----")
say_hello()
say_hello()