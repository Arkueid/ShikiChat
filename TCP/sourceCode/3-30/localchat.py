# 聊天窗口本地逻辑
import os
import time
from Client.modules.GUI.chatroom import ChatRoom
from PyQt5.QtWidgets import QMessageBox, QFileDialog


class LocalChat(ChatRoom):

    def __init__(self, user, target_user):
        super(LocalChat, self).__init__()
        self.user = user
        self.target_user = target_user
        self.setupSignals()

    def setupSignals(self):
        self.btn_send.clicked.connect(self.send)
        self.btn_clearTextEdit.clicked.connect(self.textEdit.clear)
        self.btn_clearMessages.clicked.connect(self.clearMessages)
        self.btn_downloadMessages.clicked.connect(self.saveMessages)
        self.btn_sendPicture.clicked.connect(self.sendPicture)

    def send_local(self, text):
            self.textBrowser.append(text)
            self.textEdit.clear()

    def clearMessages(self):
        if self.textBrowser.toPlainText():
            reply = QMessageBox.question(self, '删除聊天记录', '<b>所有聊天记录</b>都会被删除，\n是否继续? ',buttons=QMessageBox.Yes|QMessageBox.No,defaultButton=QMessageBox.No)
            if reply == QMessageBox.Yes:
                path = f'.\\cache\\users\\{self.user}\\_from_{self.target_user}\\messages\\'
                ls = os.listdir(path)
                for i in ls:
                    os.remove(path+i)
                self.textBrowser.clear()

    def saveMessages(self):
        messages = self.textBrowser.toHtml()
        if messages:
            path = QFileDialog.getExistingDirectory()
            if path:
                with open(path+f'\\{self.getTime("day")}_messages.html', 'wb') as f:
                    f.write(messages.encode())

    def getTime(self,by):
        if by == 'day':
            return time.strftime('%Y-%m-%d', time.localtime(int(time.time())))
        if by == 'minute':
            return time.strftime('%Y-%m-%d %H:%M', time.localtime(int(time.time())))




