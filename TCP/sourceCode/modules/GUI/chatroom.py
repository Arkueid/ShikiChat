import sys
# from PyQt5.QtCore import QSize, QRect
from PyQt5.QtGui import QIcon, QPainter, QPixmap
from PyQt5.QtWidgets import QWidget, QApplication, QPushButton, QTextEdit, QTextBrowser, QCheckBox, QGridLayout


class ChatRoom(QWidget):
    def __init__(self):
        super(ChatRoom, self).__init__()
        self.setupUi()

    def setupUi(self):

        self.resize(445, 623)
        # self.setMinimumSize(QSize(445, 623))
        # self.setMaximumSize(QSize(445, 623))
        self.setWindowTitle('Shiki-ChatRoom')
        self.setWindowIcon(QIcon('.\\texture\\icon\\ShikiSan.png'))

        self.btn_send = QPushButton()
        # self.btn_send.setGeometry(QRect(340, 580, 91, 31))

        self.btn_clearTextEdit = QPushButton()
        # self.btn_clearTextEdit.setGeometry(QRect(10, 580, 91, 31))

        self.btn_sendPicture = QPushButton()
        # self.btn_sendPicture.setGeometry(QRect(235, 580, 91, 31))

        self.textEdit = QTextEdit()
        # self.textEdit.setGeometry(QRect(10, 440, 421, 131))
        self.textEdit.setStyleSheet('background-color:rgba(255,255,255,200)')

        self.textBrowser = QTextBrowser()
        # self.textBrowser.setGeometry(QRect(10, 10, 421, 381))
        self.textBrowser.setStyleSheet('background-color:rgba(255,255,255,200)')

        self.btn_clearMessages = QPushButton()
        # self.btn_clearMessages.setGeometry(QRect(10, 400, 89, 27))

        self.btn_downloadMessages = QPushButton()
        # self.btn_downloadMessages.setGeometry(QRect(110, 400, 101, 27))

        self.checkBox = QCheckBox()
        # self.checkBox.setGeometry(QRect(320, 400, 111, 31))
        self.checkBox.setStyleSheet('background-color:rgba(255,255,255,120)')

        self.btn_send.setText("发送")
        self.btn_clearTextEdit.setText("清空")
        self.btn_sendPicture.setText("上传图片")
        self.btn_clearMessages.setText("清空记录")
        self.btn_downloadMessages.setText("保存聊天记录")
        self.checkBox.setText("缓存聊天记录")

        height = 35
        self.btn_send.setMinimumHeight(height)
        self.btn_sendPicture.setMinimumHeight(height)
        self.btn_clearTextEdit.setMinimumHeight(height)
        self.btn_clearMessages.setMinimumHeight(height)
        self.btn_downloadMessages.setMinimumHeight(height)
        self.checkBox.setMinimumHeight(height)

        self.grid = QGridLayout(self)
        self.grid.addWidget(self.textBrowser, 0,0,6,8)
        self.grid.addWidget(self.btn_clearMessages,6,0,1,1)
        self.grid.addWidget(self.btn_downloadMessages,6,6,1,1)
        self.grid.addWidget(self.checkBox,6,7,1,1)
        self.grid.addWidget(self.textEdit,7,0,3,8)
        self.grid.addWidget(self.btn_clearTextEdit,11,0,1,1)
        self.grid.addWidget(self.btn_sendPicture,11,6,1,1)
        self.grid.addWidget(self.btn_send,11,7,1,1)

    def paintEvent(self, a0) -> None:
        painter = QPainter(self)
        painter.drawPixmap(self.rect(), QPixmap('./texture/bg/bg2.png'))


if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = ChatRoom()

    def sendText():
        text = win.textEdit.toPlainText()
        win.textBrowser.insertPlainText(text)
        win.textEdit.clear()

    def clearTextEdit():
        win.textEdit.clear()

    win.btn_send.clicked.connect(sendText)
    win.btn_clearTextEdit.clicked.connect(clearTextEdit)

    win.show()
    sys.exit(app.exec_())