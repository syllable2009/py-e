#!/usr/bin/env python3
"""
Simple MCP (Model Context Protocol) Server over STDIO
Implements one tool: get_current_time
Protocol: https://github.com/modelcontextprotocol/mcp
"""

import sys
import json
import datetime
from typing import Any, Dict, List


def send_message(message: Dict[str, Any]) -> None:
    """发送 MCP 消息到 stdout（遵循 MCP 的 NDJSON 格式）"""
    line = json.dumps(message, ensure_ascii=False)
    sys.stdout.write(line + "\n")
    sys.stdout.flush()


def read_message() -> Dict[str, Any]:
    """从 stdin 读取一行 MCP 消息"""
    line = sys.stdin.readline()
    if not line:
        return {}
    return json.loads(line.strip())


def handle_initialize(params: Dict[str, Any]) -> Dict[str, Any]:
    """处理 initialize 请求，返回服务器能力"""
    return {
        "protocolVersion": "2024-10-07",
        "capabilities": {
            "tools": {
                "get_current_time": {
                    "description": "获取当前日期和时间",
                    "parameters": {
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                }
            }
        }
    }


def handle_get_current_time(args: Dict[str, Any]) -> str:
    """工具实现：返回当前时间"""
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return f"当前时间是：{now}"


def main():
    """主循环：监听 STDIO 消息并响应"""
    print("MCP 服务已启动，等待客户端连接...", file=sys.stderr)

    while True:
        try:
            msg = read_message()
            if not msg:
                break

            # MCP 消息必须包含 jsonrpc 和 id
            if msg.get("jsonrpc") != "2.0":
                continue

            method = msg.get("method")
            req_id = msg.get("id")
            params = msg.get("params", {})

            response: Dict[str, Any] = {"jsonrpc": "2.0", "id": req_id}

            if method == "initialize":
                result = handle_initialize(params)
                response["result"] = result

            elif method == "call_tool":
                tool_name = params.get("name")
                tool_args = params.get("arguments", {})

                if tool_name == "get_current_time":
                    try:
                        content = handle_get_current_time(tool_args)
                        response["result"] = {
                            "content": [{"type": "text", "text": content}]
                        }
                    except Exception as e:
                        response["error"] = {
                            "code": -32000,
                            "message": f"工具执行错误: {str(e)}"
                        }
                else:
                    response["error"] = {
                        "code": -32601,
                        "message": f"工具未找到: {tool_name}"
                    }

            elif method == "shutdown":
                response["result"] = None
                send_message(response)
                break

            else:
                response["error"] = {
                    "code": -32601,
                    "message": f"方法未实现: {method}"
                }

            send_message(response)

        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            break

    print("MCP 服务已关闭", file=sys.stderr)


if __name__ == "__main__":
    main()
    # 1.交互启动
    # {"jsonrpc":"2.0","id":1,"method":"initialize","params":{}}
    # {"jsonrpc":"2.0","id":2,"method":"call_tool","params":{"name":"get_current_time","arguments":{}}}

    # 2.echo '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"clientInfo":{"name":"test","version":"1.0"}}}' | python mcp_simple.py
    # echo '{"jsonrpc":"2.0","id":2,"method":"call_tool","params":{"name":"get_current_time","arguments":{}}}' | python mcp_simple.py