import os
import random
import sys
from .user_list_win import UserListWin
from .chatroom import ChatRoom
from .user_search_win import UserSearchWin
from .mailbox_win import MailBoxWin
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtWidgets import QFrame, QSplitter, QListWidgetItem, QApplication, QStatusBar



class MainChatWin:

    def __init__(self, user):
        self.right_chatroom_frame = QFrame()
        self.user_list_win = UserListWin(user)
        self.splitter = QSplitter(Qt.Horizontal)
        self.fri_add_page = UserSearchWin()
        self.fri_add_page.window.setParent(self.right_chatroom_frame)
        self.fri_add_page.window.setVisible(False)
        self.mailbox_page = MailBoxWin()
        self.mailbox_page.frame.setParent(self.right_chatroom_frame)
        self.mailbox_page.frame.setVisible(False)
        self.chatroom_ls = dict()
        self.current_chatroom = None
        self.setupUI()
        self.setupSignals()

    def setupUI(self):
        self.splitter.setWindowTitle('Chat')
        self.right_chatroom_frame.setMinimumSize(500, 600)
        self.right_chatroom_frame.setMaximumSize(500, 600)
        self.splitter.setMaximumSize(700, 600)
        self.splitter.setMinimumSize(700, 600)
        self.splitter.addWidget(self.user_list_win.splitter)
        self.splitter.addWidget(self.right_chatroom_frame)
        self.splitter.setSizes([150, 550])
        self.user_list_win.user_list.setIconSize(QSize(50, 50))

    def add_user(self, user, avatar, addr):
        user_item = QListWidgetItem()
        user_item.setIcon(QIcon(avatar))
        user_item.setSizeHint(QSize(70, 70))
        user_item.setText(user)
        user_item.setData(5, (user, addr))
        self.user_list_win.user_list.insertItem(0, user_item)
        _chatroom = ChatRoom()
        _chatroom.bind_item(user_item)
        _chatroom.setParent(self.right_chatroom_frame)
        self.chatroom_ls[user] = _chatroom
        _chatroom.setVisible(False)
        return _chatroom

    def setupSignals(self):
        self.user_list_win.user_list.clicked.connect(self.show_chatroom)
        self.user_list_win.action_add_fri.triggered.connect(self.show_fri_add_page)
        self.user_list_win.notice_btn.clicked.connect(self.show_mailbox_page)

    def show_chatroom(self):
        data = self.user_list_win.user_list.currentItem().data(5)
        user = data[0]
        if self.current_chatroom:
            self.current_chatroom.setVisible(False)
        self.current_chatroom = self.chatroom_ls[user]
        self.current_chatroom.setVisible(True)
        self.splitter.setWindowTitle('to '+user)

    def show_fri_add_page(self):
        if self.current_chatroom:
            self.current_chatroom.setVisible(False)
        self.fri_add_page.window.setVisible(True)
        self.current_chatroom = self.fri_add_page.window

    def show_mailbox_page(self):
        if self.current_chatroom:
            self.current_chatroom.setVisible(False)
        self.mailbox_page.frame.setVisible(True)
        self.current_chatroom = self.mailbox_page.frame


if __name__ == '__main__':
    def _send():
        global test
        chatroom: ChatRoom = test.current_chatroom
        text = chatroom.textEdit.toPlainText()
        chatroom.add_item('artoria', test.user_list_win.user_list.currentItem().data(5)[0], type_='send', content=text)
        chatroom.add_item('artoria', test.user_list_win.user_list.currentItem().data(5)[0], type_='receive',
                          content=text)
        chatroom.textEdit.clear()


    def update_avatar():
        global test
        root = 'D:/MyDocument/Pictures/fgo/'
        file = random.choice(os.listdir(root))
        chatroom: ChatRoom = test.current_chatroom
        a: QListWidgetItem = chatroom.bound_item
        a.setIcon(QIcon(root + file))
        test.user_list_win.profile.avatar.clear()
        test.user_list_win.profile.avatar.setPixmap(QPixmap(root + file))
    app = QApplication(sys.argv)
    test = MainChatWin('Antoneva')
    chatroom = test.add_user('Artoria', r'C:\Users\ArcueidBrunestud\Desktop\ShikiChat\TCP\shiki_splited\__client__\Client\texture\icon\5243fbf2b2119313e32bc12b62380cd790238dc4.jpg', '')
    chatroom.btn_send.clicked.connect(_send)
    chatroom = test.add_user('Antoneva', r'C:\Users\ArcueidBrunestud\Desktop\ShikiChat\TCP\shiki_splited\__client__\Client\texture\bg\bg8.jpg', '')
    chatroom.btn_send.clicked.connect(_send)
    test.user_list_win.profile.btn_eidt.clicked.connect(update_avatar)
    test.splitter.show()
    sys.exit(app.exec_())