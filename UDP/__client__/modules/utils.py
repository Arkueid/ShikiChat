import time
from PyQt5.QtCore import QObject, pyqtSignal


class Signals(QObject):
    receive_message = pyqtSignal(tuple)
    receive_online_users = pyqtSignal()
    receive_profile = pyqtSignal(dict)
    receive_avatar = pyqtSignal(str)
    doubleClicked = pyqtSignal()
    receive_fri_req = pyqtSignal(tuple)
    receive_fri_req_accepted = pyqtSignal(tuple)
    fri_already_warning = pyqtSignal(str)


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