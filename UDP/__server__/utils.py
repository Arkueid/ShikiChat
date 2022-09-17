import time


def get_curr_time(by='sec'):
    if by == 'min':
        return time.strftime('%Y-%m-%d %H:%M', time.localtime(time.time()))
    elif by == 'hour':
        return time.strftime('%Y-%m-%d %H', time.localtime(time.time()))
    elif by == 'sec':
        return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
    elif by == 'day':
        return time.strftime('%Y-%m-%d', time.localtime(time.time()))


if __name__ == '__main__':
    a = get_curr_time("day").replace("-", "/")
    print(a)