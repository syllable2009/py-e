from mydemo.spider.platform.bilibili import BilibiliCrawler
from mydemo.spider.platform.tieba.tieba import TiebaShuCrawler
from mydemo.spider.platform.xcode.xcode import XCodeCrawler
from mydemo.spider.platform.xiaohongshu.xhs import XiaoHongShuCrawler
from mydemo.spider.platform.zhihu import ZhihuCrawler
import mydemo.spider.platform
import asyncio
import sys
import signal
from signal import SIGINT, SIGTERM
from typing import Iterable, Optional, Sequence, Type, TypeVar


async def async_cleanup():
    """异步清理函数，用于处理CDP浏览器等异步资源"""
    global crawler
    if crawler:
        # 检查并清理CDP浏览器
        if hasattr(crawler, 'cdp_manager') and crawler.cdp_manager:
            try:
                await crawler.cdp_manager.cleanup(force=True)  # 强制清理浏览器进程
            except Exception as e:
                # 只在非预期错误时打印
                error_msg = str(e).lower()
                if "closed" not in error_msg and "disconnected" not in error_msg:
                    print(f"[Main] 清理CDP浏览器时出错: {e}")

        # 检查并清理标准浏览器上下文（仅在非CDP模式下）
        elif hasattr(crawler, 'browser_context') and crawler.browser_context:
            try:
                # 检查上下文是否仍然打开
                if hasattr(crawler.browser_context, 'pages'):
                    await crawler.browser_context.close()
            except Exception as e:
                # 只在非预期错误时打印
                error_msg = str(e).lower()
                if "closed" not in error_msg and "disconnected" not in error_msg:
                    print(f"[Main] 关闭浏览器上下文时出错: {e}")

    # 关闭数据库连接
    # if config.SAVE_DATA_OPTION in ["db", "sqlite"]:
    #     await db.close()


def cleanup():
    """同步清理函数"""
    try:
        # 创建新的事件循环来执行异步清理
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(async_cleanup())
        loop.close()
    except Exception as e:
        print(f"[Main] 清理时出错: {e}")


def signal_handler(signum, _frame):
    """信号处理器，处理Ctrl+C等中断信号"""
    print(f"\n[Main] 收到中断信号 {signum}，正在清理资源...")
    cleanup()
    sys.exit(0)


class SpiderFactory(object):
    CRAWLERS = {
        "bili": BilibiliCrawler,
        "zhihu": ZhihuCrawler,
        "xhs": XiaoHongShuCrawler,
        "tieba": TiebaShuCrawler,
        "xcode": XCodeCrawler,
    }

    @staticmethod
    def create_spider_obj(platform: str):
        crawler_class = SpiderFactory.CRAWLERS.get(platform)
        if not crawler_class:
            raise ValueError(
                "Invalid Media Platform Currently only supported bili or zhihu ..."
            )
        # 实例化执行init方法
        return crawler_class()


async def parse_cmd(argv: Optional[Sequence[str]] = None):
    pass


if __name__ == "__main__":
    # 注册信号处理器
    # signal.signal(signal.SIGINT, signal_handler)   # Ctrl+C
    # signal.signal(signal.SIGTERM, signal_handler)  # # kill 命令 (Unix) 终止信号
    #
    # crawler = SpiderFactory.create_spider_obj("zhihu")
    # print(crawler)
    # crawler.start()
    parse_cmd()
