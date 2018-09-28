# -*- coding: utf-8 -*-

import sys
from threated_crawler import thread_crawler
from mongo_cache import MongoCache
from alexa_callback import AlexaCallback


def main(max_threads):
    scrape_callback = AlexaCallback()
    cache = MongoCache()
    # cache.clear()
    thread_crawler(scrape_callback.seed_url, scrape_callback=scrape_callback, cache=cache, max_threads=max_threads,
                   timeout=10)


if __name__ == '__main__':
    # max_threads = int(sys.argv[1])  # 需要在terminal运行；
    # main(max_threads)
    main(10)
