#!/usr/bin/python3
# 今日はいい天気ですね！
# Welcome back, ArcueidBrunestud!
# Let's start coding!
import sys

from PySide6.QtCore import QSize
from PySide6.QtWidgets import QWidget, QListWidget, QListWidgetItem, QApplication, QPushButton, QLineEdit, QGridLayout
from PySide6.QtGui import QIcon, QPixmap


class UserSearchWin:

    def __init__(self):
        self.window = QWidget()
        self.led_search = QLineEdit()
        self.btn_search = QPushButton('搜索')
        self.btn_add_fri_req = QPushButton('添加好友')
        self.result_ls = QListWidget()
        self.grid = QGridLayout(self.window)
        self.setupUI()

    def setupUI(self):
        self.window.setWindowTitle('查找用户')
        self.window.setMaximumSize(500, 400)
        self.window.setMinimumSize(500, 400)
        self.led_search.setPlaceholderText('请输用户UID或昵称')
        self.led_search.setFixedHeight(30)
        self.btn_search.setFixedHeight(30)
        self.grid.addWidget(self.led_search, 0, 0, 1, 2)
        self.grid.addWidget(self.btn_search, 0, 2, 1, 1)
        self.grid.addWidget(self.btn_add_fri_req, 0, 3, 1, 1)
        self.grid.addWidget(self.result_ls, 1, 0, 4, 4)
        self.result_ls.setIconSize(QSize(50, 50))

    def add_result(self, account_id, avatar):
        item = QListWidgetItem(account_id)
        item.setIcon(avatar)
        item.setSizeHint(QSize(70, 70))
        self.result_ls.addItem(item)
        return item


if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = UserSearchWin()
    pixmap = QPixmap(r'C:\Users\ArcueidBrunestud\Desktop\ShikiChat\UDP\__client__\.local\data\Ass123\avatar\0f9681899936c2c9d6af0224c5b0ee2f.png')
    item = win.add_result('123', QIcon(pixmap))
    win.window.show()
    sys.exit(app.exec_())