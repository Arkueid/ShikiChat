import sys
from .user_profile_item import UserItem
from PySide6.QtWidgets import QListWidget, QApplication, QSplitter, QListWidgetItem, QVBoxLayout, QToolButton, QFrame, QHBoxLayout, QPushButton
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QIcon, QAction


class UserListWin:

    def __init__(self, user):
        self.user = user
        self.action_add_fri = QAction('添加好友')
        self.action_logout = QAction('退出登录')
        self.setupUI()

    def setupUI(self):
        self.splitter = QSplitter(Qt.Vertical)
        self.splitter.setMinimumSize(200, 600)
        self.splitter.setMaximumSize(200, 600)
        self.user_list = QListWidget()
        self.profile = UserItem(self.user)
        self.profile.setMinimumSize(200, 70)
        self.profile.setMaximumSize(200, 70)
        self.opt_btn = QToolButton()
        self.opt_btn.setText('更多操作')
        self.frame = QFrame()
        self.opt_btn.setMaximumSize(150, 30)
        self.opt_btn.setMinimumSize(150, 30)
        self.opt_btn.setPopupMode(QToolButton.InstantPopup)
        self.hbox = QHBoxLayout()
        self.notice_btn = QPushButton('✉')
        self.notice_btn.setStyleSheet('font: 30px')
        self.notice_btn.setFixedHeight(30)
        self.notice_btn.setFixedWidth(30)
        self.hbox.addWidget(self.opt_btn)
        self.hbox.addWidget(self.notice_btn)
        self.vbox = QVBoxLayout(self.frame)
        self.vbox.addWidget(self.user_list)
        self.vbox.addLayout(self.hbox)
        self.splitter.addWidget(self.profile)
        self.splitter.addWidget(self.frame)
        self.opt_btn.addAction(self.action_add_fri)
        self.opt_btn.addAction(self.action_logout)
        self.opt_btn.setStyleSheet(f'width: 150px')


if __name__ == '__main__':
    app = QApplication(sys.argv)
    test = UserListWin('hello')
    item = QListWidgetItem()
    item.setIcon(QIcon(
        r'C:\Users\ArcueidBrunestud\Desktop\ShikiChat\TCP\shiki_splited\__client__\Client\texture\bg\entrance_bg.jpg'))
    test.user_list.setIconSize(QSize(70, 70))
    item.setSizeHint(QSize(70, 70))
    item.setText('Antoneva')
    test.user_list.addItem(item)
    test.splitter.show()
    sys.exit(app.exec_())

