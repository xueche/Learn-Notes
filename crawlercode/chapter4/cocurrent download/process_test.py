# -*- coding: utf-8 -*-

import sys
from process_crawler import process_crawler
from mongo_cache import MongoCache
from alexa_callback import AlexaCallback


def main(max_threads):
    scrape_callback = AlexaCallback()
    # cache = MongoCache()
    # cache.clear()
    process_crawler(scrape_callback.seed_url, scrape_callback=scrape_callback, max_threads=max_threads,
                    timeout=10)


if __name__ == '__main__':
    # max_threads = int(sys.argv[1])
    # main(max_threads)
    main(10)
