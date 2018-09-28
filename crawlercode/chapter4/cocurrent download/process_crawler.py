# -*- coding: utf-8

import time
import threading
import multiprocessing
from mongo_queue import MongoQueue
from downloader import Downloader
from mongo_cache import MongoCache

SLEEP_TIME = 1


def threaded_crawler(seed_url, delay=5, cache=MongoCache(), scrape_callback=None, user_agent='wswp',
                     proxies=None, num_retries=1, max_threads=10, timeout=10):
    """Crawl using multiple threads"""
    # the queue of url's that still need to be crawled
    crawl_queue = MongoQueue()
    crawl_queue.clear()
    crawl_queue.push(seed_url)
    D = Downloader(cache=cache, delay=delay, user_agent=user_agent, proxies=proxies, num_retries=num_retries,
                   timeout=timeout)

    def process_queue():
        while True:
            # keep track that are processing url
            try:
                url = crawl_queue.pop()
            except KeyError:
                # currently no urls to process
                break
            else:
                html = D(url)
                if scrape_callback:
                    try:
                        links = scrape_callback(url, html) or []
                    except Exception as e:
                        print 'Error in callback for; {}:{}'.format(url, e)
                    else:
                        for link in links:
                            # add this new link to queue
                            crawl_queue.push(link)
                crawl_queue.complete(url)

    # wait for all download threads to finish
    threads = []
    while threads or crawl_queue:
        for thread in threads:
            if not thread.is_alive():
                threads.remove(thread)
        while len(threads) < max_threads and crawl_queue.peek():
            thread = threading.Thread(target=process_queue)
            thread.setDaemon(True)
            thread.start()
            threads.append(thread)
        time.sleep(SLEEP_TIME)    # 线程睡眠1s


def process_crawler(args, **kwargs):    # **kwargs表示关键字参数，它是一个字典；*args表示任意个参数，是一个turple,元组
    num_cpus = multiprocessing.cpu_count()
    # pool = multiprocessing.Pool(processes=num_cpus)
    print 'Starting {} processes'.format(num_cpus)
    start = time.time()
    processes = []
    # result = []
    for i in range(num_cpus):
        p = multiprocessing.Process(target=threaded_crawler, args=[args], kwargs=kwargs)
        # target:指定进程执行的函数，args:该函数的参数，需要使用tuple
        # result.append(pool.apply_async(threaded_crawler, args, kwargs))
        p.start()
    # pool.close()
    # pool.join()
    # for res in result:
        # print res.get()
        processes.append(p)
    # wait for processes to complete
    for p in processes:
         p.join()             # 阻塞当前进程，直到调用join方法的那个进程执行完，再继续执行当前进程。
    end = time.time()
    print 'total: %.2f seconds' % (end - start)


