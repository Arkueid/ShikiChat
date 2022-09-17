import time
from modules.GUI.chatroom import ChatRoom
from PyQt5.QtWidgets import QMessageBox, QFileDialog


class Chat(ChatRoom):

    def __init__(self, user):
        super(Chat, self).__init__()
        self.user = user
        self.setupSignals()

    def setupSignals(self):
        self.btn_send.clicked.connect(self.send)
        self.btn_clearTextEdit.clicked.connect(self.textEdit.clear)
        self.btn_clearMessages.clicked.connect(self.clearMessages)
        self.btn_downloadMessages.clicked.connect(self.saveMessages)
        self.btn_sendPicture.clicked.connect(self.sendPicture)

    def send(self):
        text = self.textEdit.toHtml()
        if self.textEdit.toPlainText():
            text = f'<u>{self.user}</u> {self.getTime("minute")}<p>'+text+'</p><br>'
            self.textBrowser.insertHtml(text)
            self.textEdit.clear()

    def clearMessages(self):
        if self.textBrowser.toPlainText():
            reply = QMessageBox.question(self, '删除信息记录', '是否删除信息记录? ',buttons=QMessageBox.Yes|QMessageBox.No,defaultButton=QMessageBox.No)
            if reply == QMessageBox.Yes:
                self.textBrowser.clear()

    def saveMessages(self):
        messages = self.textBrowser.toHtml()
        if messages:
            path = QFileDialog.getExistingDirectory()
            if path:
                with open(path+f'\\{self.getTime("day")}_messages.html', 'ab') as f:
                    f.write(messages.encode())

    def sendPicture(self):
        path, _ = QFileDialog.getOpenFileName(self,"打开图片",filter="*.jpg;;*.png;;*.webp;;*.gif;;All Files(*)")
        if path:
            self.textEdit.append(f'<br><img src="{path}"></img><br>')

    def getTime(self,by):
        if by == 'day':
            return time.strftime('%Y-%m-%d', time.localtime(int(time.time())))
        if by == 'minute':
            return time.strftime('%Y/%m/%d %H:%M', time.localtime(int(time.time())))




