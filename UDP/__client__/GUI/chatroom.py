import sys
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QWidget, QPushButton, QTextEdit, QCheckBox, QGridLayout, \
    QSplitter, QFrame, QHBoxLayout, QListWidget, QListWidgetItem,  QAbstractItemView
from PyQt5.QtCore import Qt
from .messagebox import MessageBox


class ChatRoom(QWidget):

    def __init__(self):
        super(ChatRoom, self).__init__()
        self.MAXIMUM: int = 0
        self.setupUi()

    def setupUi(self):

        self.resize(500, 600)
        self.setWindowIcon(QIcon('./texture/icon/ShikiSan.ico'))

        self.btn_send = QPushButton()

        self.btn_clearTextEdit = QPushButton()

        self.btn_sendPicture = QPushButton()

        self.textEdit = QTextEdit()
        self.textEdit.setStyleSheet('font:12pt;background-color:rgba(255,255,255,100)')

        self.messageList = QListWidget()
        self.messageList.setStyleSheet('background-color:rgba(255,255,255,100)')
        self.messageList.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.messageList.setSelectionMode(QAbstractItemView.NoSelection)

        self.btn_clearMessages = QPushButton()

        self.checkBox = QCheckBox()
        self.checkBox.setStyleSheet('background-color:rgba(255,255,255,100);border-radius:10px;border:2px solid rgb(230,230,230);border-style:outset')

        self.btn_send.setText("发送")
        self.btn_clearTextEdit.setText("清空")
        self.btn_sendPicture.setText("发送图片")
        self.btn_clearMessages.setText("删除聊天记录")
        self.checkBox.setText("缓存聊天记录")

        height = 35
        self.btn_send.setMinimumHeight(height)
        self.btn_sendPicture.setMinimumHeight(height)
        self.btn_clearTextEdit.setMinimumHeight(height)
        self.btn_clearMessages.setMinimumHeight(height)
        self.checkBox.setMinimumHeight(height)

        self.spliter = QSplitter(Qt.Vertical,self)
        self.frame1 = QFrame()
        self.grid = QGridLayout(self.frame1)
        self.grid.addWidget(self.messageList, 0,0,8,8)
        self.grid.addWidget(self.btn_clearMessages,8,0,1,1)
        self.grid.addWidget(self.checkBox,8,7,1,1)
        self.frame2 = QFrame()
        self.grid2 = QGridLayout(self.frame2)
        self.grid2.addWidget(self.textEdit,0,0,1,8)
        self.grid2.addWidget(self.btn_clearTextEdit,1,0,1,1)
        self.grid2.addWidget(self.btn_sendPicture,1,6,1,1)
        self.grid2.addWidget(self.btn_send,1,7,1,1)

        self.spliter.addWidget(self.frame1)
        self.spliter.addWidget(self.frame2)
        self.spliter.setSizes([500,225])

        self.main_hbox = QHBoxLayout(self)
        self.main_hbox.addWidget(self.spliter)

    def bind_item(self, item):
        self.bound_item = item

    def add_item(self, sender, receiver, type_="receive", content_type="text", content=None, avatar=''):
        if type_ == "receive":
            item = QListWidgetItem()
            w = MessageBox(sender, receiver, self.bound_item.icon().pixmap(50, 50, QIcon.Normal, QIcon.Off),
                           type_, content_type, content)
            item.setSizeHint(w.sizeHint())
            self.messageList.addItem(item)
            self.messageList.setItemWidget(item, w)
        else:
            item = QListWidgetItem()
            w = MessageBox(sender, receiver, avatar, 'send',
                           content_type, content)
            item.setSizeHint(w.sizeHint())
            self.messageList.addItem(item)
            self.messageList.setItemWidget(item, w)


if __name__ == '__main__':
    from PyQt5.QtWidgets import QApplication
    app = QApplication(sys.argv)
    i = QListWidgetItem()
    i.setIcon(QIcon('../default.png'))
    print()
    win = ChatRoom()
    win.bind_item(i)
    win.add_item('artoria', 'shiki', content='hi')

    win.show()
    sys.exit(app.exec_())