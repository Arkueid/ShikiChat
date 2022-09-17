#!/usr/bin/python3
# 今日はいい天気ですね！
# Welcome back, ArcueidBrunestud!
# Let's start coding!
import sys

from PyQt5.QtWidgets import QApplication, QWidget, QListWidgetItem, QListWidget, QPushButton, QLabel, QGridLayout, QFrame, QVBoxLayout
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import QSize, pyqtSignal


class btn(QPushButton):
    clicked = pyqtSignal(tuple)
    d = (None, )

    def mousePressEvent(self, e) -> None:
        self.clicked.emit(self.d)

    def set_emit_data(self, v):
        self.d = v


class MailBoxListItemUIForm:

    def __init__(self, uid: str, avatar):
        self.accept_btn = btn('同意')
        self.reject_btn = btn('拒绝')
        self.uid_label = QLabel(uid)
        self.avatar = QLabel()
        self.avatar.setPixmap(avatar)
        self.setupUI()

    def setupUI(self):
        self.form = QWidget()
        grid = QGridLayout(self.form)
        self.avatar.setFixedSize(70, 70)
        self.uid_label.setFixedSize(100, 30)
        self.accept_btn.setFixedSize(100, 25)
        self.reject_btn.setFixedSize(100, 25)
        grid.addWidget(self.avatar, 0, 0, 2, 2)
        grid.addWidget(self.uid_label, 0, 2, 1, 2)
        grid.addWidget(self.accept_btn, 0, 5, 1, 1)
        grid.addWidget(self.reject_btn, 1, 5, 1, 1)


class MailBoxWin:

    def __init__(self):
        self.frame = QFrame()
        self.mail_ls = QListWidget()
        self.vbox = QVBoxLayout(self.frame)
        self.title = QLabel('消息列表')
        self.setupUI()

    def setupUI(self):
        self.frame.setFixedSize(500, 600)
        self.vbox.addWidget(self.title)
        self.vbox.addWidget(self.mail_ls)

    def add_mail(self, uid, avatar, addr, idx):
        UI_form = MailBoxListItemUIForm(uid, avatar)
        item = QListWidgetItem()
        item.setSizeHint(QSize(100, 85))
        item.setData(5, uid)
        UI_form.accept_btn.set_emit_data((uid, True, addr, idx))
        UI_form.accept_btn.clicked.connect(self.remove_item)
        UI_form.reject_btn.set_emit_data((uid, False, addr, idx))
        UI_form.reject_btn.clicked.connect(self.remove_item)
        self.mail_ls.addItem(item)
        self.mail_ls.setItemWidget(item, UI_form.form)
        return UI_form

    def remove_item(self, data):
        for idx in range(self.mail_ls.count()):
            if self.mail_ls.item(idx).data(5) == data[0]:
                self.mail_ls.takeItem(idx)
                return



if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = MailBoxWin()
    win.add_mail('hello', QPixmap(r'C:\Users\ArcueidBrunestud\Desktop\ShikiChat\UDP\__client__\.local\data\Jack12\avatar\ee2be38b845877078775f4ddec31b2fc.png'), 2)
    win.frame.show()
    sys.exit(app.exec_())

