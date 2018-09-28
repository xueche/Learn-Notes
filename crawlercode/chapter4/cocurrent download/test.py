# encoding:utf-8

import multiprocessing
import os, time, random


# 线程启动后实际执行的代码块
def r1(process_name, test=5):
    for i in range(5):
        print process_name, test, os.getpid()  # 打印出当前进程的id
        time.sleep(random.random())


def r2(process_name):
    for i in range(5):
        print process_name, os.getpid()  # 打印出当前进程的id
        time.sleep(random.random())


if __name__ == "__main__":
    print "main process run..."
    num_cpus = multiprocessing.cpu_count()
    processes = []
    for i in range(num_cpus):
        p = multiprocessing.Process(target=r1, args=('process_name1',))
        # target:指定进程执行的函数，args:该函数的参数，需要使用tuple
        p.start()
        processes.append(p)
    # wait for processes to complete
    for p in processes:
        p.join()  # 阻塞当前进程，直到调用join方法的那个进程执行完，再继续执行当前进程。


    print "main process runned all lines..."