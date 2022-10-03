import time
from PySide6.QtCore import QObject, Signal


class Signals(QObject):
    receive_message = Signal(tuple)
    receive_online_users = Signal()
    receive_profile = Signal(dict)
    receive_avatar = Signal(str)
    doubleClicked = Signal()
    receive_fri_req = Signal(tuple)
    receive_fri_req_accepted = Signal(tuple)
    fri_already_warning = Signal(str)


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
    a = get_curr_time('sec')
    print(a)