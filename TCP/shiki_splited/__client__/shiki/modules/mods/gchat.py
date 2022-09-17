""""
本地聊天逻辑
"""
import hashlib
import json
import os
import struct
import sys
import time
import bs4
from PIL import Image
from PyQt5.QtWidgets import QMessageBox, QFileDialog, QListWidgetItem
from PyQt5.QtCore import pyqtSignal, Qt
from .connector import Client
from ..GUI import MessageBox, ChatRoom


class GChat(ChatRoom):
    pictureSent = pyqtSignal(QListWidgetItem)
    textSent = pyqtSignal(QListWidgetItem)

    def __init__(self,user: str, target_user: str, client: Client, message_type="message"):
        """

        :param user: str
        :param target_user: str
        :param client: Client
        :param message_type: "message"|"public-message"
        """
        super(GChat, self).__init__()
        self.user = user

        self.setupSignals()

        self.currentUsers: list = []
        self.Client = client
        self.message_type = message_type
        self.target_user = target_user
        self.setWindowTitle(f"ShikiChatRoom {self.user}-->{self.target_user}")

        self.initialize()

        headers = {"code":0, "type":"RFA","target": "server","avatar-user":self.target_user,"sender":self.user}
        headers = json.dumps(headers,ensure_ascii=False).encode('utf-8-sig')
        self.Client.send(struct.pack('i',len(headers)))
        self.Client.send(headers)
        ls = os.listdir(self.rootPath + 'messages')
        if 'AUTOSAVE' in ls:
            ls.remove('AUTOSAVE')
        for i in ls:
            soup = bs4.BeautifulSoup(open(self.rootPath+'messages/'+i,'rb+').read(),'lxml')
            for i in soup.body:
                if i.attrs['content-type'] == "text":
                    message = i.text
                    item = QListWidgetItem()
                    lw = MessageBox(i.attrs['sender'],i.attrs['receiver'], type_=i.attrs['type'], content_type=i.attrs['content-type'], content=message)
                    item.setSizeHint(lw.grid.sizeHint())
                    self.messageList.addItem(item)
                    self.messageList.setItemWidget(item, lw)
                elif i.attrs['content-type'] == "image":
                    message = str(i)
                    item = QListWidgetItem()
                    lw = MessageBox(i.attrs['sender'], i.attrs['receiver'], type_=i.attrs['type'], content_type=i.attrs['content-type'],
                                    content=message)
                    item.setSizeHint(lw.grid.sizeHint())
                    self.messageList.addItem(item)
                    self.messageList.setItemWidget(item, lw)
        else:
            item = QListWidgetItem('以上为历史消息')
            item.setTextAlignment(Qt.AlignHCenter)
            self.messageList.addItem(item)
        if os.path.exists(self.rootPath+'messages/'+'AUTOSAVE'):
            self.AutoSave = open(self.rootPath+'messages/'+'AUTOSAVE','r+').read()
        else:
            self.AutoSave = '1'
        if self.AutoSave == '1':
            self.checkBox.setChecked(True)

    def setupSignals(self):
        self.btn_send.clicked.connect(self.send)
        self.btn_send.clicked.connect(lambda : self.messageList.verticalScrollBar().setValue(self.messageList.verticalScrollBar().maximum()))
        self.btn_sendPicture.clicked.connect(
            lambda: self.messageList.verticalScrollBar().setValue(self.messageList.verticalScrollBar().maximum()))
        self.btn_clearTextEdit.clicked.connect(self.textEdit.clear)
        self.btn_clearMessages.clicked.connect(self.clearMessages)
        self.btn_sendPicture.clicked.connect(self.sendPicture)
        self.checkBox.toggled.connect(self.isAutoSave)
        self.pictureSent.connect(self.autoSaveMessage)
        self.textSent.connect(self.autoSaveMessage)

    def clearMessages(self):
        if self.messageList.count():
            reply = QMessageBox.question(self, '删除聊天记录', '<b>所有聊天记录</b>都会被删除，\n是否继续? ',buttons=QMessageBox.Yes|QMessageBox.No,defaultButton=QMessageBox.No)
            if reply == QMessageBox.Yes:
                path = f'./Client/cache/users/{self.user}/_from_{self.target_user}/messages/'
                ls = os.listdir(path)
                for i in ls:
                    os.remove(path+i)
                self.messageList.clear()

    def send_local(self, text):
            lw = MessageBox(self.user, self.target_user, 'send', content_type="text", content=text)
            item = QListWidgetItem()
            item.setSizeHint(lw.grid.sizeHint())
            self.messageList.addItem(item)
            self.messageList.setItemWidget(item, lw)
            self.textEdit.clear()
            self.textSent.emit(item)

    def send(self):
        text = self.textEdit.toPlainText()
        if text != '':
            message = text.encode()
            headers = {"code": 0,"type": self.message_type, "content-type": "text", "content-length": len(message), "sender": f"{self.user}",
                       "target": self.target_user,
                       'st': self.getTime('minute')}
            headers = json.dumps(headers,ensure_ascii=False).encode('utf-8-sig')
            try:
                self.Client.send(struct.pack('i', len(headers)))
                self.Client.send(headers)
                self.Client.send(message)
            except:
                QMessageBox.warning(self, '断开连接', '与服务器中断连接!\n请重新启动客户端', buttons=QMessageBox.Close)
                if not self.Client._closed:
                    self.Client.close()
                return 1
            self.send_local(text)

    def sendPicture(self):
        path, _ = QFileDialog.getOpenFileName(self,"打开图片",filter="*.jpg;;*.png;;*.webp;;*.gif;;")
        if path:
            image = open(path,'rb').read()
            reply = QMessageBox.information(self, '发送图片', '是否发送图片？', buttons=QMessageBox.Yes | QMessageBox.No)
            if reply == QMessageBox.No:
                return 1
            image_name = path.split('/')[-1]
            content_type = 'image/.'+image_name.split('.')[-1]
            content_length = len(image)
            headers = {"code": 0, "type": self.message_type, "content-type": content_type,
                       "content-length": content_length, "sender": f"{self.user}",
                       "target": self.target_user,
                       "md5": hashlib.md5(image).hexdigest(), 'st': self.getTime('minute')}
            headers = json.dumps(headers,ensure_ascii=False).encode('utf-8-sig')
            try:
                self.Client.send(struct.pack('i',len(headers)))
                self.Client.send(headers)
            except:
                QMessageBox.warning(self, '断开连接', '与服务器中断连接!\n请重新启动客户端', buttons=QMessageBox.Close)
                return 1
            self.Client.send(image)
            img = Image.open(path)
            message = f'<img src="{path}" sender="{self.user}" receiver="{self.target_user}" type="send" content-type="image" width="300" height="{300/img.width*img.height}"></img>'
            item = QListWidgetItem()
            lw = MessageBox(self.user,self.target_user, type_="send", content_type="image", content=message)
            item.setSizeHint(lw.grid.sizeHint())
            self.messageList.addItem(item)
            self.messageList.setItemWidget(item, lw)
            self.pictureSent.emit(item)

    def isAutoSave(self):
        if self.checkBox.isChecked():
            with open(self.rootPath+'messages/''AUTOSAVE','w') as f:
                f.write('1')
        else:
            with open(self.rootPath+'messages/'"AUTOSAVE",'w') as f:
                f.write('')

    def autoSaveMessage(self, item):
        if not self.checkBox.isChecked():
            return
        # print(item.text(),bool(item.text()))
        if item.text():
            return
        message = self.messageList.itemWidget(item).message.text()
        path = f'./Client/cache/users/{self.user}/_from_{self.target_user}/messages/'
        if not os.path.exists(path):
            os.mkdir(path)
        with open(path+f'/{self.getTime("day")}_messages.html','ab+') as f:
            f.write(message.encode('utf-8'))

    def getTime(self, by):
        if by == 'day':
            return time.strftime('%Y-%m-%d', time.localtime(int(time.time())))
        if by == 'minute':
            return time.strftime('%Y-%m-%d %H:%M', time.localtime(int(time.time())))

    def initialize(self):
        self.rootPath = f'./Client/cache/users/{self.user}/_from_{self.target_user}/'
        if not os.path.exists(self.rootPath):
            os.mkdir(self.rootPath)
        if not os.path.exists(self.rootPath + 'messages'):
            os.mkdir(self.rootPath + 'messages')
        if not os.path.exists(self.rootPath + 'images/avatar'):
            os.makedirs(self.rootPath + 'images/avatar')


if __name__ == '__main__':
    from PyQt5.QtWidgets import QApplication
    app = QApplication(sys.argv)
    chat = GChat('Shiki', 'Artoria', Client())
    chat.Client.login('Shiki', '123456')


    chat.show()
    # chat.startReceiver()
    app.exec_()
    sys.exit()