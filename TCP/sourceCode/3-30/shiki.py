import os.path
import sys

from PyQt5.QtGui import QPainter, QPixmap

from .gchat import GChat
from threading import Thread
from .client import Client
import json, struct, time
from PyQt5.QtWidgets import QMessageBox, QWidget, QSplitter, QApplication, QListWidget, QVBoxLayout, QLabel, \
    QListWidgetItem, QFrame
from PyQt5.QtCore import Qt, pyqtSignal, QSize
import hashlib
from PIL import Image


class Shiki(QWidget):
    userListChanged = pyqtSignal()
    getMessage = pyqtSignal(str)
    userOffline = pyqtSignal(str)
    connectionClosed = pyqtSignal()

    def __init__(self,user,client: Client):
        super(Shiki, self).__init__()
        self.onlineUsers: list = []
        self.currentUsers: list = []
        self.Client = client
        self.hasMessage = '（有新消息）'
        self.ChatRooms = dict()
        self.user = user
        self.rootPath = f".\\cache\\users\\{self.user}\\"
        if not os.path.exists(self.rootPath):
           os.mkdir(self.rootPath)
        self.setupUI()
        self.setupSignals()

    def setupSignals(self):
        self.userListChanged.connect(self.updateUserList)
        self.userList.clicked.connect(self.showChatRoom)
        self.getMessage.connect(self.messageNotice)
        self.userOffline.connect(self.clearOfflinedUser)
        self.connectionClosed.connect(self.showConnectionClosed)

    def setupUI(self):
        self.resize(800,650)
        self.setWindowTitle(f"ShikiChatRoom-{self.user}")

        self.onshow = QFrame()

        self.userList = QListWidget()
        title = QListWidgetItem('在线用户')
        self.userList.setStyleSheet('background-color:rgba(255,255,255,200)')
        title.setData(1, None)
        self.userList.addItem(title)

        self.currentChatRoom = self.onshow

        self.spliter = QSplitter(Qt.Horizontal)

        self.spliter.addWidget(self.userList)
        self.spliter.addWidget(self.onshow)
        self.spliter.setSizes([200,600])

        self.main_vbox = QVBoxLayout(self)
        self.main_vbox.addWidget(self.spliter)

    def runClient(self):
        sendHeartbeat = Thread(target=self.sendHeartbeat, daemon=True)
        receiver = Thread(target=self.receive, daemon=True)
        sendHeartbeat.start()
        receiver.start()

    def receive(self):
        while True:
            try:
                headers_len = struct.unpack('i',self.Client.recv(4))[0]
                headers = self.Client.recv(headers_len).decode('utf-8-sig')
            except:
                print('Disconnected by server!')
                self.Client.close()
                self.connectionClosed.emit()
                break
            headers = json.loads(headers)
            if headers['code'] == 1:
                break
            if headers['type'] == "message":
                if headers['content-type'] == "text":
                    content_length = headers['content-length']
                    message = b''
                    t = content_length
                    while t != 0:
                        if t < 1024:
                            chunk = self.Client.recv(t)
                        else:
                            chunk = self.Client.recv(1024)
                        message += chunk
                        t -= len(chunk)
                    message = message.decode()
                    message = f'<h3><font style="font-family:STKaiTi"><b>{headers["user"]}</b></font> <font size="3">{headers["st"]}</font></h3>' \
                                f'<font style="font-family:Apple LiGothic Medium" size="4">'+message+'</font>'
                    self.ChatRooms[headers['user']].textBrowser.append(message)
                    self.getMessage.emit(headers['user'])
                elif "image" in headers['content-type']:
                    content_type = headers['content-type'].split('/')[-1]
                    content_length = headers['content-length']
                    path = f'C:\\Users\\ArcueidBrunestud\\Desktop\\ShikiChat\\Client\\cache\\users\\{self.currentChatRoom.user}\\_from_{self.currentChatRoom.target_user}\\' + 'images\\'
                    if not os.path.exists(path):
                        os.mkdir(path)
                    file_name = f'{headers["md5"]}{content_type}'
                    message = b''
                    with open(f'{path}{file_name}', 'wb') as f:
                        t = content_length
                        while t != 0:
                            if t < 1024:
                                chunk = self.Client.recv(t)
                            else:
                                chunk = self.Client.recv(1024)
                            f.write(chunk)
                            message += chunk
                            t -= len(chunk)
                    print(headers['md5'] == hashlib.md5(message).hexdigest())
                    img = Image.open(path+file_name)
                    message = f'<h3><font style="font-family:STKaiTi"><b>{headers["user"]}</b></font> <font size="3">{headers["st"]}</font></h3>' \
                              f'<br><img src="{path+file_name}" width="{400}" height="{400/img.width*img.height}"></img>'
                    self.getMessage.emit(headers['user'])
                    self.currentChatRoom.textBrowser.append(message)
            elif headers['type'] == "current users":
                self.onlineUsers = headers['cu']
                print(self.onlineUsers)
                self.userListChanged.emit()

            elif headers['type'] == "offline":
                self.userOffline.emit(headers['target'])

    def sendHeartbeat(self):
        while True:
            try:
                text = f'{self.getTime("minute")}'.encode()
                headers = {"code": 0, "type": "heartbeat", "content-type": "heartbeat", "content-length": len(text), "user": f"{self.user}",
                           'st':self.getTime('minute')}
                headers = json.dumps(headers,ensure_ascii=False).encode('utf-8-sig')
                self.Client.send(struct.pack('i', len(headers)))
                self.Client.send(headers)
                self.Client.send(text)
                time.sleep(60)
            except:
                self.connectionClosed.emit()
                print('connection failed')
                self.Client.close()
                break

    def getTime(self, by):
        if by == 'day':
            return time.strftime('%Y-%m-%d', time.localtime(int(time.time())))
        if by == 'minute':
            return time.strftime('%Y-%m-%d %H:%M', time.localtime(int(time.time())))

    def closeEvent(self, a0) -> None:
        if self.Client._closed:
            return
        headers = json.dumps({"code": 1,"type":"close",'st':self.getTime('minute')}).encode('utf-8-sig')
        self.Client.send(struct.pack('i',len(headers)))
        self.Client.send(headers)

    def updateUserList(self):
        for i in self.onlineUsers:
            if i not in self.currentUsers:
                item = QListWidgetItem(i)
                item.setSizeHint(QSize(100,60))
                item.setData(1, i)
                self.userList.addItem(item)
                # self.userList.setItemWidget(item, userItem(i))
                self.ChatRooms[i]=GChat(self.user,i,self.Client)
        self.currentUsers = self.onlineUsers
        for i in range(1,self.userList.count()):
            item = self.userList.item(i)
            if item:
                user = item.data(1)
            else:
                continue
            if user not in self.currentUsers:
                self.userList.takeItem(i)
                del self.ChatRooms[user]

    def showChatRoom(self):
        user = self.userList.currentItem().data(1)
        if self.hasMessage in self.userList.currentItem().text():
            self.userList.currentItem().setText(user)
        if user:
            self.currentChatRoom.setVisible(False)
            self.currentChatRoom = self.ChatRooms[user]
            self.spliter.addWidget(self.currentChatRoom)
            self.currentChatRoom.setVisible(True)
            self.setWindowTitle(f"ShikiChatRoom-{self.user}"+'-->'+user)
        else:
            self.currentChatRoom.setVisible(False)
            self.currentChatRoom = self.onshow
            self.spliter.addWidget(self.currentChatRoom)
            self.onshow.setVisible(True)
            self.setWindowTitle(f"ShikiChatRoom-{self.user}")

    def messageNotice(self, user):
        for i in range(1,self.userList.count()):
            if self.userList.item(i).data(1) == user:
                self.userList.item(i).setText(user + self.hasMessage)
                break

    def paintEvent(self, a0) -> None:
        painter = QPainter(self)
        painter.drawPixmap(self.rect(), QPixmap('./texture/bg/bg5.png'))

    def clearOfflinedUser(self,user):
        QMessageBox.information(None, '提示', user + "已下线!", buttons=QMessageBox.Ok)
        for i in range(1,self.userList.count()):
            if self.userList.item(i).data(1) == user:
                del self.ChatRooms[user]
                self.currentUsers.remove(user)
                self.userList.takeItem(i)

    def showConnectionClosed(self):
        QMessageBox.warning(self,'断开连接', '与服务器中断连接!\n请重新启动客户端', buttons=QMessageBox.Close)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = Shiki('Shiki',Client())
    win.Client.login('Shiki',"I-LOVE-SHIKI")
    win.runClient()
    win.show()
    app.exec_()
    sys.exit()
