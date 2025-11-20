import uvicorn
from fastapi import FastAPI, Request, HTTPException
from pydantic import BaseModel
from typing import Any, Dict, List, Optional, Union
import datetime
import uuid

app = FastAPI(title="MCP over HTTP", description="Model Context Protocol via HTTP/JSON")

# ===== 工具注册表 =====
TOOLS = {}

def register_tool(name: str, description: str, parameters: dict):
    def decorator(func):
        TOOLS[name] = {
            "func": func,
            "description": description,
            "parameters": parameters
        }
        print(f"Registered tool: {name}")
        return func
    return decorator


def register_tool2(name: str, description: str, parameters: dict):
    def decorator(func):
        # 定义一个包装函数，每次调用 func 时都会经过它
        def wrapper(args: dict):
            print(f"🔧 正在调用工具: {name}")  # ← 每次调用都会执行！
            # 你还可以在这里加：
            # - 日志记录
            # - 参数校验
            # - 调用计数
            # - 异常捕获
            result = func(args)
            print(f"✅ 工具 {name} 执行完成")
            return result

        # 注册的是 wrapper，不是原函数
        TOOLS[name] = {
            "func": wrapper,  # ← 关键：注册 wrapper
            "description": description,
            "parameters": parameters
        }
        print(f"📌 工具已注册: {name}")  # 这个仍然只在定义时打印一次
        return func  # 可选：是否让原函数保持“干净”
    return decorator

def my_decorator(func):
    def wrapper(*args, **kwargs):
        print("Calling function:", func.__name__)
        return func(*args, **kwargs)
    return wrapper

# ===== 示例工具：获取当前时间 =====
# 装饰器在函数定义时（模块加载时）就执行
# 如果你希望 每次调用函数时都执行装饰器中的逻辑（比如打印日志、记录耗时、鉴权等），那么你需要让装饰器返回一个 包装函数（wrapper），而不是直接返回原函数。
@register_tool2(
    name="get_current_time",
    description="获取当前日期和时间",
    parameters={
        "type": "object",
        "properties": {},
        "required": []
    }
)
def get_current_time(args: dict) -> str:
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return f"当前时间是：{now}"

# ===== 示例工具：简单计算器 =====
@register_tool(
    name="add_numbers",
    description="将两个数字相加",
    parameters={
        "type": "object",
        "properties": {
            "a": {"type": "number", "description": "第一个数字"},
            "b": {"type": "number", "description": "第二个数字"}
        },
        "required": ["a", "b"]
    }
)
def add_numbers(args: dict) -> str:
    a = args.get("a", 0)
    b = args.get("b", 0)
    result = a + b
    return f"{a} + {b} = {result}"

# ===== 请求/响应模型 =====
class JsonRpcRequest(BaseModel):
    jsonrpc: str = "2.0"
    method: str
    params: Optional[Dict[str, Any]] = None
    id: Union[str, int]

class JsonRpcResponse(BaseModel):
    jsonrpc: str = "2.0"
    id: Union[str, int]
    result: Optional[Dict[str, Any]] = None
    error: Optional[Dict[str, Any]] = None

# ===== 工具调用结果格式（MCP 规范）=====
def make_mcp_content(text: str) -> dict:
    return {
        "content": [
            {"type": "text", "text": text}
        ]
    }

# ===== MCP HTTP 端点 =====
@app.post("/mcp", response_model=JsonRpcResponse)
async def mcp_endpoint(request: Request, rpc_req: JsonRpcRequest):
    if rpc_req.jsonrpc != "2.0":
        raise HTTPException(status_code=400, detail="Only JSON-RPC 2.0 supported")

    response = {"jsonrpc": "2.0", "id": rpc_req.id}

    try:
        if rpc_req.method == "initialize":
            # 返回服务器能力
            capabilities = {
                "tools": {
                    name: {
                        "description": tool["description"],
                        "parameters": tool["parameters"]
                    }
                    for name, tool in TOOLS.items()
                }
            }
            response["result"] = {
                "protocolVersion": "2024-10-07",
                "capabilities": capabilities
            }

        elif rpc_req.method == "call_tool":
            if not rpc_req.params or "name" not in rpc_req.params:
                raise ValueError("Missing 'name' in call_tool params")

            tool_name = rpc_req.params["name"]
            tool_args = rpc_req.params.get("arguments", {})

            if tool_name not in TOOLS:
                response["error"] = {
                    "code": -32601,
                    "message": f"Tool not found: {tool_name}"
                }
            else:
                try:
                    tool_func = TOOLS[tool_name]["func"]
                    # func
                    result_text = tool_func(tool_args)
                    response["result"] = make_mcp_content(result_text)
                except Exception as e:
                    response["error"] = {
                        "code": -32000,
                        "message": f"Tool execution failed: {str(e)}"
                    }

        elif rpc_req.method == "shutdown":
            response["result"] = None

        else:
            response["error"] = {
                "code": -32601,
                "message": f"Method not implemented: {rpc_req.method}"
            }

    except Exception as e:
        response["error"] = {
            "code": -32603,
            "message": f"Internal error: {str(e)}"
        }

    return response

# ===== 健康检查 =====
@app.get("/")
async def root():
    return {"message": "MCP over HTTP is running", "tools": list(TOOLS.keys())}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

