# -*- coding: utf-8 -*-

import itertools
from commom import download


def iteration():
    num_errors = 0
    for page in itertools.count(1):
    # 使用itertools中的count()生成一个无限迭代器
        url = 'http://example.webscraping.com/view/-{}'.format(page)
        html = download(url)
        if html is None:
            num_errors += 1
            if num_errors > 5:        #连续5次下载错误才会停止遍历ID
                break
        else:
            num_errors = 0


if __name__ == '__main__':
    iteration()