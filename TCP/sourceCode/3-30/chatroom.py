import sys
# from PyQt5.QtCore import QSize, QRect
from PyQt5.QtGui import QIcon, QPainter, QPixmap
from PyQt5.QtWidgets import QWidget, QApplication, QPushButton, QTextEdit, QTextBrowser, QCheckBox, QGridLayout, \
    QSplitter, QFrame, QHBoxLayout
from PyQt5.QtCore import Qt


class ChatRoom(QWidget):
    def __init__(self):
        super(ChatRoom, self).__init__()
        self.setupUi()

    def setupUi(self):

        self.resize(600, 650)
        # self.setMinimumSize(QSize(445, 623))
        # self.setMaximumSize(QSize(445, 623))
        self.setWindowIcon(QIcon('.\\texture\\icon\\ShikiSan.ico'))

        self.btn_send = QPushButton()
        # self.btn_send.setGeometry(QRect(340, 580, 91, 31))

        self.btn_clearTextEdit = QPushButton()
        # self.btn_clearTextEdit.setGeometry(QRect(10, 580, 91, 31))

        self.btn_sendPicture = QPushButton()
        # self.btn_sendPicture.setGeometry(QRect(235, 580, 91, 31))

        self.textEdit = QTextEdit()
        # self.textEdit.setGeometry(QRect(10, 440, 421, 131))
        self.textEdit.setStyleSheet('font:12pt;background-color:rgba(255,255,255,200)')

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
        self.btn_sendPicture.setText("发送图片")
        self.btn_clearMessages.setText("删除聊天记录")
        self.btn_downloadMessages.setText("保存聊天记录")
        self.checkBox.setText("缓存聊天记录")

        height = 35
        self.btn_send.setMinimumHeight(height)
        self.btn_sendPicture.setMinimumHeight(height)
        self.btn_clearTextEdit.setMinimumHeight(height)
        self.btn_clearMessages.setMinimumHeight(height)
        self.btn_downloadMessages.setMinimumHeight(height)
        self.checkBox.setMinimumHeight(height)

        self.spliter = QSplitter(Qt.Vertical,self)
        self.frame1 = QFrame()
        self.grid = QGridLayout(self.frame1)
        self.grid.addWidget(self.textBrowser, 0,0,8,8)
        self.grid.addWidget(self.btn_clearMessages,8,0,1,1)
        self.grid.addWidget(self.btn_downloadMessages,8,6,1,1)
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

    # def paintEvent(self, a0) -> None:
    #     painter = QPainter(self)
    #     painter.drawPixmap(self.rect(), QPixmap('./texture/bg/bg5.png'))


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