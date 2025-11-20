MCP（Model Context Protocol）是由 LangChain、LlamaIndex 等生态推动的一种标准化协议，用于让 LLM 应用与外部工具、数据源、记忆系统等进行结构化交互。
其核心思想类似于 “LLM 调用函数”，但通过统一的 JSON-RPC 风格接口暴露能力。
MCP 协议本身是文本协议，我们用 Python 标准库即可实现。

JSON-RPC 是一种 轻量级的远程过程调用（RPC）协议，使用 JSON 格式在客户端和服务器之间传递调用请求和结果。
基本特点：
所有消息都是 合法的 JSON 对象
每条消息包含：
"jsonrpc": "2.0"：标识协议版本
"method"：要调用的函数名（字符串）
"params"：参数（对象或数组，可选）
"id"：请求 ID（用于匹配请求与响应，通知类请求可省略）

{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "initialize",
  "params": {
    "clientInfo": {
      "name": "Cursor",
      "version": "0.45.0"
    }
  }
}

{
  "jsonrpc": "2.0",
  "id": 2,
  "method": "call_tool",
  "params": {
    "name": "get_weather",
    "arguments": {
      "city": "北京"
    }
  }
}

工具返回必须用 { "content": [...] } 结构