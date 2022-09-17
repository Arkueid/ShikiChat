import os
import sys

from PyQt5.QtWidgets import QLabel, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt


class MessageBox(QWidget):

    def __init__(self, sender, receiver, type_="receive", content_type="text", content=None):
        super(MessageBox, self).__init__()
        self.sender = sender
        self.receiver = receiver
        self.content_type = content_type
        self.content = content
        self.type = type_
        if type_ == "receive":
            self.avatarPath = f"./Client/cache/users/{self.receiver}/_from_{self.sender}/images/avatar/{self.sender}.avatar"
        elif type_ == "send":
            self.avatarPath = f"./Client/cache/users/{self.sender}/avatar/MyAvatar.jpg"

        self.setupUI()
        # print(self.message.text())

    def setupUI(self):
        self.stylesheet_receiver = 'font:14px "微软雅黑";border-style:outset;border:10px solid rgb(200,200,230);border-top-right-radius:20px;border-bottom-right-radius:20px;border-bottom-left-radius:20px;background-color:rgb(200,200,230)'
        self.stylesheet_sender = 'font:14px "微软雅黑";border:10px solid rgb(130,130,210);border-top-left-radius:20px;border-bottom-right-radius:20px;border-bottom-left-radius:20px;background-color:rgb(130,130,210)'

        if self.content_type == "text":
            text = self.content.replace('\n', '<br>')
            text = list(text)
            for idx, item in enumerate(text):
                if (idx) % 30 == 0 and idx != 0:
                    text.insert(idx, '<br>')
            text = ''.join(text)
            self.message = QLabel()
            self.message.adjustSize()
            self.message.setAlignment(Qt.AlignVCenter)
            self.message.setMaximumWidth(430)
            self.message.setText(
                f'<p type="{self.type}" sender="{self.sender}" receiver="{self.receiver}" content-type="{self.content_type}">{text}</p>')
            self.message.setStyleSheet(self.stylesheet_sender if self.type == "send" else self.stylesheet_receiver)
            self.message.setTextInteractionFlags(Qt.TextSelectableByMouse)

        elif self.content_type == "image":
            self.message = QLabel(self.content)
            self.message.setAlignment(Qt.AlignVCenter)
            self.message.setMaximumWidth(430)
            self.message.adjustSize()
            self.message.setStyleSheet(self.stylesheet_sender if self.type == "send" else self.stylesheet_receiver)
            self.message.setTextInteractionFlags(Qt.TextSelectableByMouse)

        self.avatar = QLabel()
        if os.path.exists(self.avatarPath):
            self.avatar.setPixmap(QPixmap(self.avatarPath))
        else:
            self.avatar.setPixmap(QPixmap(""))
        self.avatar.setMinimumSize(50, 50)
        self.avatar.setMaximumSize(50, 50)
        self.avatar.setScaledContents(True)
        self.avatar.setStyleSheet("border:1px solid rgba(230,230,230,150);border-style:inset")

        self.username = QLabel(f'<font style="font-family:微软雅黑;color:black" size="3"><b>{self.sender}</b></font>')
        self.username.setMaximumSize(200, 15)
        self.username.setMinimumSize(200, 15)
        self.username.setStyleSheet('background-color:transparent')

        if self.type == "receive":
            self.grid = QGridLayout(self)
            self.grid.addWidget(self.username, 0, 1, 1, 1)
            self.vbox = QVBoxLayout()
            self.vbox.addWidget(self.avatar)
            self.vbox.addStretch(0)
            self.grid.addLayout(self.vbox, 0, 0, 2, 1)
            # self.grid.addWidget(self.avatar,0,0,2,1)
            self.hbox = QHBoxLayout()
            self.hbox.addWidget(self.message)
            self.hbox.addStretch(0)
            self.grid.addLayout(self.hbox, 1, 1, 2, 1)
            # self.grid.addWidget(self.message,1,1,2,1)
        else:
            self.grid = QGridLayout(self)
            self.username.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.grid.addWidget(self.username, 0, 1, 1, 1)
            self.vbox = QVBoxLayout()
            self.vbox.addWidget(self.avatar)
            self.vbox.addStretch(0)
            self.grid.addLayout(self.vbox, 0, 2, 2, 1)
            # self.grid.addWidget(self.avatar,0,2,2,1)
            self.hbox = QHBoxLayout()
            self.hbox.addStretch(0)
            self.hbox.addWidget(self.message)
            self.grid.addLayout(self.hbox, 1, 0, 2, 2)
            # self.grid.addWidget(self.message,1,0,2,2)


if __name__ == '__main__':
    from PyQt5.QtWidgets import QApplication

    app = QApplication(sys.argv)
    win2 = MessageBox(sender="Artoria", receiver="Shiki", type_="send", content="Shit")
    win2.show()
    print(win2.size())
    app.exec_()
    sys.exit()
