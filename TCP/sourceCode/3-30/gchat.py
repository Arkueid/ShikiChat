import hashlib
import json
import os
import struct
import sys

import bs4
from PIL import Image
from PyQt5.QtWidgets import QApplication, QMessageBox, QFileDialog
from .localchat import LocalChat
from .client import Client
from Client.modules.mods.localchat import LocalChat


class GChat(LocalChat):

    def __init__(self,user, target_user, client: Client):
        super(GChat, self).__init__(user=user,target_user=target_user)
        self.currentUsers: list = []
        self.Client = client
        self.target_user = target_user
        self.checkBox.toggled.connect(self.isAutoSave)
        self.setWindowTitle(f"ShikiChatRoom {self.user}-->{self.target_user}")
        self.rootPath = f'.\\cache\\users\\{self.user}\\_from_{self.target_user}\\'
        if not os.path.exists(self.rootPath):
            os.mkdir(self.rootPath)
        if not os.path.exists(self.rootPath+'images'):
            os.mkdir(self.rootPath+'images')
        if not os.path.exists(self.rootPath+'messages'):
            os.mkdir(self.rootPath+'messages')
        ls = os.listdir(self.rootPath + 'messages')
        for i in ls:
            self.textBrowser.insertHtml(open(self.rootPath+'messages\\'+i,'rb+').read().decode('utf-8'))
        self.textBrowser.textChanged.connect(self.autoSaveMessage)
        if os.path.exists(self.rootPath+'messages\\'+'AUTOSAVE'):
            self.AutoSave = open(self.rootPath+'messages\\'+'AUTOSAVE','r+').read()
        else:
            self.AutoSave = ''
        print(self.AutoSave)
        if self.AutoSave:
            self.checkBox.toggle()

    # def receive(self):
    #     while True:
    #         try:
    #             headers_len = struct.unpack('i',self.Client.recv(4))[0]
    #             headers = self.Client.recv(headers_len).decode('utf-8-sig')
    #         except:
    #             print('Disconnected by server!')
    #             self.Client.close()
    #             QMessageBox.warning(None, '断开连接', '与服务器中断连接!\n请重新启动客户端', buttons=QMessageBox.Close)
    #             break
    #         headers = json.loads(headers)
    #         if headers['code'] == 1:
    #             break
    #         if headers['type'] == "message":
    #             if headers['content-type'] == "text":
    #                 content_length = headers['content-length']
    #                 message = b''
    #                 t = content_length
    #                 while t != 0:
    #                     if t < 1024:
    #                         chunk = self.Client.recv(t)
    #                     else:
    #                         chunk = self.Client.recv(1024)
    #                     message += chunk
    #                     t -= len(chunk)
    #                 message = message.decode()
    #                 message = f'<h3><font style="font-family:STKaiTi"><b>{headers["user"]}</b></font> <font size="3">{headers["st"]}</font></h3>' \
    #                             f'<font style="font-family:Apple LiGothic Medium" size="4">'+message+'</font>'
    #                 self.textBrowser.append(message)
    #             elif "image" in headers['content-type']:
    #                 content_type = headers['content-type'].split('/')[-1]
    #                 content_length = headers['content-length']
    #                 path = os.getcwd() + f'\\cache\\users\\{self.user}\\_from_{self.target_user}\\' + 'images\\'
    #                 if not os.path.exists(path):
    #                     os.mkdir(path)
    #                 file_name = f'{headers["md5"]}{content_type}'
    #                 message = b''
    #                 with open(f'{path}{file_name}', 'wb') as f:
    #                     t = content_length
    #                     while t != 0:
    #                         if t < 1024:
    #                             chunk = self.Client.recv(t)
    #                         else:
    #                             chunk = self.Client.recv(1024)
    #                         f.write(chunk)
    #                         message += chunk
    #                         t -= len(chunk)
    #                 print(headers['md5'] == hashlib.md5(message).hexdigest())
    #                 img = Image.open(path+file_name)
    #                 message = f'<h3><font style="font-family:STKaiTi"><b>{headers["user"]}</b></font> <font size="3">{headers["st"]}</font></h3>' \
    #                           f'<br><img src="{path+file_name}" width="{400}" height="{400/img.width*img.height}"></img>'
    #                 self.textBrowser.append(message)
    #         # elif headers['type'] == "current users":
    #         #     self.currentUsers = headers['cu']
    #         #     print(self.currentUsers)

    # def startReceiver(self):
        # t = Thread(target=self.receive,daemon=True)
        # t2 = Thread(target=self.sendHeartbeat,daemon=True)
        # t.start()
        # t2.start()

    def send(self):
        soup = bs4.BeautifulSoup(self.textEdit.toPlainText(),'lxml')
        text = str(soup)
        if text:
            text = text.replace("\n", "<br>").replace('\\','')
            print(self.textEdit.toMarkdown())
            message = text.encode()
            headers = {"code": 0,"type": "message", "content-type": "text", "content-length": len(message), "user": f"{self.user}",
                       "target": self.target_user,
                       'st':self.getTime('minute')}
            headers = json.dumps(headers,ensure_ascii=False).encode('utf-8-sig')
            try:
                self.Client.send(struct.pack('i',len(headers)))
                self.Client.send(headers)
                self.Client.send(message)
            except:
                QMessageBox.warning(self, '断开连接', '与服务器中断连接!\n请重新启动客户端', buttons=QMessageBox.Close)
                if not self.Client._closed:
                    self.Client.close()
                return 1
            text = f'<h3><font style="font-family:STKaiTi"><b>{self.user}</b></font> <font size="3">{self.getTime("minute")}</font></h3>' \
                   f'<font style="font-family:Apple LiGothic Medium" size="4">'+text+'</font>'
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
            headers = {"code": 0, "type": "message", "content-type": content_type,
                       "content-length": content_length,"user": f"{self.user}",
                       "target": self.target_user,
                       "md5": hashlib.md5(image).hexdigest(),'st': self.getTime('minute')}
            headers = json.dumps(headers,ensure_ascii=False).encode('utf-8-sig')
            try:
                self.Client.send(struct.pack('i',len(headers)))
                self.Client.send(headers)
            except:
                QMessageBox.warning(self, '断开连接', '与服务器中断连接!\n请重新启动客户端', buttons=QMessageBox.Close)
                return 1
            self.Client.send(image)
            img = Image.open(path)
            message = f'<h3><font style="font-family:STKaiTi"><b>{self.user}</b></font> <font size="3">{self.getTime("minute")}</font></h3>' \
                      f'<br><img src="{path}" width="400" height="{400/img.width*img.height}"></img>'
            self.textBrowser.append(message)

    # def closeEvent(self, a0) -> None:
    #     if self.Client._closed:
    #         return
    #     headers = json.dumps({"code": 1,"type":"close",'st':self.getTime('minute')}).encode('utf-8-sig')
    #     self.Client.send(struct.pack('i',len(headers)))
    #     self.Client.send(headers)

    def isAutoSave(self):
        self.AutoSave = not self.AutoSave
        if self.AutoSave:
            with open(self.rootPath+'messages\\''AUTOSAVE','w') as f:
                f.write('1')
        else:
            with open(self.rootPath+'messages\\'"AUTOSAVE",'w') as f:
                f.write('')

    def autoSaveMessage(self):
        if not self.AutoSave:
            return
        message = self.textBrowser.toHtml()
        path = f'.\\cache\\users\\{self.user}\\_from_{self.target_user}\\messages\\'
        if not os.path.exists(path):
            os.mkdir(path)
        with open(path+f'\\{self.getTime("day")}_messages.html','wb') as f:
            f.write(message.encode('utf-8'))


if __name__ == '__main__':
    app = QApplication(sys.argv)
    chat = GChat('Shiki', 'Artoria',Client())
    chat.Client.login('Shiki','I-LOVE-SHIKI')
    chat.show()
    chat.startReceiver()
    app.exec_()
    sys.exit()