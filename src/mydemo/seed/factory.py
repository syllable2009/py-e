from mydemo.seed.platform.suno.suno import SunoCrawler
from mydemo.seed.service import AbstractCrawler


class SpiderFactory(object):
    CRAWLERS = {
        "suno": SunoCrawler,
    }

    @staticmethod
    def create_spider_obj(platform: str) -> AbstractCrawler:
        crawler_class = SpiderFactory.CRAWLERS.get(platform)
        if not crawler_class:
            raise ValueError(
                "Invalid Media Platform Currently not supported ..."
            )
        # 实例化执行init方法
        return crawler_class()
