import signal
import asyncio

from mydemo.seed import config
from mydemo.seed.factory import SpiderFactory

# 全局变量用于控制关闭
shutdown_event = asyncio.Event()


async def main():
    """主协程"""
    print("[Main] 程序启动，按 Ctrl+C 退出")
    global crawler
    # 通过静态工厂获取实例
    crawler = SpiderFactory.create_spider_obj(platform=config.PLATFORM)
    print(type(crawler))
    await crawler.start_with_playwright()



async def async_cleanup():
    """真正的异步清理逻辑"""
    print("[Cleanup] 正在关闭资源...")
    # 示例：关闭 aiohttp client、数据库连接、取消任务等
    await asyncio.sleep(0.1)  # 模拟异步操作
    print("[Cleanup] 清理完成")


def ask_exit():
    """信号回调：设置关闭事件"""
    print("\n[Signal] 收到中断信号，准备退出...")
    shutdown_event.set()


if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    # 注册信号处理器（仅 Unix）
    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, ask_exit)

    try:
        loop.run_until_complete(main())
    finally:
        # 确保清理只执行一次
        loop.run_until_complete(async_cleanup())
        loop.close()
        print("[Main] 程序已退出")
