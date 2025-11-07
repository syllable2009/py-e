from fastapi import APIRouter
from fastapi.responses import StreamingResponse
import asyncio
import json,uuid
from datetime import datetime

user_router = APIRouter()

@user_router.get("/user")
def user_root():
    return {"user": "ok"}

async def event_generator(conversation_id: str, timestamp: int):
    """生成 SSE 事件流"""
    # id校验
    # 名为 message_event:{conversation_id} 的有序集合中，取出分数（score）大于等于 offset 的所有成员（member）
    # REDIS_CLIENT.zrangebyscore(name=f"message_event:{conversation_id}", min=offset, max="+inf",withscores=True)

    count = 0
    while count < 10:
        count += 1
        data = {
            "id": count,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "data": f"第 {count} 条消息",
            "event": "data"
        }
        # SSE 格式：以 "data: " 开头，结尾两个换行符
        yield f"data: {json.dumps(data, ensure_ascii=False)}\n\n"
        # await asyncio.sleep(0.2)  # 每秒发送一次

    # 可选：发送一个结束标志
    yield "event: end\ndata: {\"message\": \"stream ended\"}\n\n"




@user_router.get("/sse")
def sse():
    return StreamingResponse(
        event_generator("id", None),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",  # 禁用 Nginx 缓冲（如有）
        }
    )
