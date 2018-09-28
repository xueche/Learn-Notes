# -*- coding:utf-8 -*_

import itertools
from commom import download


def iteration():
    for page in itertools.count(1):
        url = 'http://example.webscraping.com/view/-%d' % page
        html= download(url)
        if html is None:
            break
        else:
            # success - can scrape the result
            pass


if __name__ == '__main__':
    print iteration()


