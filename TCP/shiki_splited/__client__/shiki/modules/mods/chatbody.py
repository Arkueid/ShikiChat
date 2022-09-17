"""
聊天窗口主体
"""
import hashlib
import json
import os.path
import struct
import sys
import time
from threading import Thread

from PIL import Image
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QPainter, QPixmap
from PyQt5.QtWidgets import QMessageBox, QWidget, QSplitter, QListWidget, QVBoxLayout, \
    QListWidgetItem, QFrame, QLabel, QHBoxLayout, QPushButton, QFileDialog
from .connector import Client
from .gchat import GChat
from ..GUI import MessageBox, UserItem


class ChatBody(QWidget):
    userListChanged = pyqtSignal()
    getMessage = pyqtSignal(tuple)
    userOffline = pyqtSignal(str)
    connectionClosed = pyqtSignal()
    timeCount = pyqtSignal()
    infoUpdated = pyqtSignal(tuple)

    def __init__(self, user: str, client: Client):
        super(ChatBody, self).__init__()
        self.onlineUsers: list = []
        self.currentUsers: list = []
        self.Client = client
        self.ChatRooms = dict()
        self.user = user
        self.rootPath = f"Client/cache/users/{self.user}/"
        if not os.path.exists(self.rootPath):
            os.mkdir(self.rootPath)
        if not os.path.exists(self.rootPath + "avatar"):
            os.mkdir(self.rootPath + "avatar")
        avatar = os.listdir(self.rootPath + "avatar/")
        if len(avatar) != 0:
            self.avatarPath = self.rootPath + "avatar/"+avatar[0]
        else:
            self.avatarPath = None
        self.setupUI()
        self.setupSignals()
        self.uploadInfo()

    def setupSignals(self):
        self.userListChanged.connect(self.updateUserList)
        self.userList.clicked.connect(self.showChatRoom)
        self.getMessage.connect(self.messageNotice)
        self.userOffline.connect(self.clearOfflinedUser)
        self.connectionClosed.connect(self.showConnectionClosed)
        self.getMessage.connect(self.drawMessage)
        self.btn_editProfile.clicked.connect(self.setMyAvatar)
        self.timeCount.connect(self.showTime)
        self.infoUpdated.connect(self.updateInfo)

    def setupUI(self):
        self.resize(850, 700)
        self.setWindowTitle(f"ShikiChatRoom-{self.user}")

        self.onshow = QFrame()

        self.userList = QListWidget()
        title = QListWidgetItem()
        title.setText('在线用户')
        title.setTextAlignment(Qt.AlignHCenter)
        self.userList.setStyleSheet('background-color:rgba(255,255,255,100)')
        title.setData(1, None)
        self.userList.addItem(title)

        self.publicChat = QListWidgetItem()
        self.publicChat.setTextAlignment(Qt.AlignHCenter)
        self.userList.addItem(self.publicChat)
        self.publicChat.setData(1,"%all%")
        lw = UserItem(self.user,"%all%",self.publicChat,self.userList)
        lw.clicked.connect(self.showChatRoom)
        self.publicChat.setSizeHint(lw.sizeHint())
        self.ChatRooms["%all%"]= GChat(self.user, "%all%", self.Client, message_type="public-message")
        self.userList.setItemWidget(self.publicChat,lw)
        self.currentUsers.append("%all%")

        self.currentChatRoom = self.onshow

        self.avatar = QLabel()
        self.avatar.setMinimumSize(70, 70)
        self.avatar.setMaximumSize(70, 70)
        self.btn_editProfile = QPushButton('编辑头像')
        if self.avatarPath:
            self.avatar.setPixmap(QPixmap(self.avatarPath))
        else:
            pixmap = QPixmap(70, 70)
            pixmap.fill(Qt.white)
            self.avatar.setPixmap(pixmap)
        self.avatar.setScaledContents(True)
        self.avatar.setStyleSheet("border:1px solid rgba(230,230,230,150);border-style:inset")

        self.sub_hbox = QHBoxLayout()  # 用户信息栏布局
        self.sub_hbox.addWidget(self.avatar)
        self.sub_hbox_sub_vbox = QVBoxLayout()
        self.nameTitle = QLabel(self.user)
        self.nameTitle.setStyleSheet('color:rgb(230,230,230);font:20px "华光粗黑_CNKI"')
        self.nameTitle.setAlignment(Qt.AlignVCenter)
        self.sub_hbox_sub_vbox.addWidget(self.nameTitle)
        self.sub_hbox_sub_vbox.addWidget(self.btn_editProfile)
        self.sub_hbox.addLayout(self.sub_hbox_sub_vbox)

        self.user_vbox = QVBoxLayout()
        self.user_vbox.addLayout(self.sub_hbox)
        self.user_vbox.addWidget(self.userList)
        self.userFrame = QFrame()
        self.userFrame.setLayout(self.user_vbox)

        self.spliter = QSplitter(Qt.Horizontal)
        self.spliter.addWidget(self.userFrame)
        self.spliter.addWidget(self.onshow)
        self.spliter.setSizes([200, 600])

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
                headers_len = struct.unpack('i', self.Client.recv(4))[0]
                headers = self.Client.recv(headers_len).decode('utf-8-sig')
            except Exception as e:
                print(e)
                self.connectionClosed.emit()
                print('Disconnected by server!')
                self.Client.close()
                break
            headers = json.loads(headers)
            print(headers)
            if headers['code'] == 1:
                break
            if headers['type'] in ["message","public-message"] :
                if headers['type'] == "message":
                    ChatRoom = headers['sender']
                elif headers['type'] == "public-message":
                    ChatRoom = "%all%"
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
                    self.getMessage.emit((headers['sender'], headers['target'], message, headers['content-type'], ChatRoom))
                elif "image" in headers['content-type']:
                    content_type = headers['content-type'].split('/')[-1]
                    content_length = headers['content-length']
                    path = f'./Client/cache/users/{self.user}/_from_{headers["sender"]}/' + 'images/'
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
                    img = Image.open(path + file_name)
                    message = f'<img src="{path + file_name}" sender="{headers["sender"]}" receiver="{headers["target"]}" type="receive" content-type="image" width="{300}" height="{300 / img.width * img.height}"></img>'
                    self.getMessage.emit((headers['sender'], headers['target'], message, headers['content-type'], ChatRoom))
            elif headers['type'] == "current users":
                self.onlineUsers = headers['cu']
                self.userListChanged.emit()

            elif headers['type'] == "offline":
                self.userOffline.emit(headers['target'])

            elif headers['type'] == "RFA":
                with open( f'./Client/cache/users/{self.user}/avatar/MyAvatar.avatar', 'rb') as f:
                    img = f.read()
                headers = {"code": 0, "type": "avatar", "content-type": "image/.avatar", "content-length": len(img),
                           "target": headers["sender"],
                           "user": self.user, "md5": hashlib.md5(img).hexdigest()}
                headers = json.dumps(headers, ensure_ascii=False).encode('utf-8-sig')
                self.Client.send(struct.pack('i', len(headers)))
                self.Client.send(headers)
                self.Client.send(img)

            elif headers['type'] == "avatar":
                content_type = headers['content-type'].split('/')[-1]
                content_length = headers['content-length']
                path = f'./Client/cache/users/{self.user}/_from_{headers["avatar-user"]}/' + 'images/avatar/'
                if not os.path.exists(path):
                    os.mkdir(path)
                file_name = f'{headers["avatar-user"]}{content_type}'
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
                self.infoUpdated.emit((headers['avatar-user'],))

    def sendHeartbeat(self):
        while True:
            try:
                text = f'{self.getTime("YmdHM")}'.encode()
                headers = {"code": 0, "type": "heartbeat", "content-type": "heartbeat", "content-length": len(text),
                           "sender": f"{self.user}",
                           'st': self.getTime('YmdHM')}
                headers = json.dumps(headers, ensure_ascii=False).encode('utf-8-sig')
                self.Client.send(struct.pack('i', len(headers)))
                self.Client.send(headers)
                self.Client.send(text)
                time.sleep(60)
                self.timeCount.emit()
            except:
                self.connectionClosed.emit()
                print('connection failed')
                self.Client.close()
                break

    def getTime(self, by):
        if by == 'Ymd':
            return time.strftime('%Y-%m-%d', time.localtime(int(time.time())))
        elif by == 'YmdHM':
            return time.strftime('%Y-%m-%d %H:%M', time.localtime(int(time.time())))
        elif by == 'HM':
            return time.strftime('%H:%M', time.localtime(int(time.time())))

    def closeEvent(self, a0) -> None:
        if self.Client._closed:
            return
        headers = json.dumps({"code": 1, "type": "close","sender":self.user ,'st': self.getTime('YmdHM')}).encode('utf-8-sig')
        self.Client.send(struct.pack('i', len(headers)))
        self.Client.send(headers)

    def updateUserList(self):
        for i in self.onlineUsers:
            if i not in self.currentUsers and i != "%all%":
                item = QListWidgetItem()
                lw = UserItem(self.user, i, item, self.userList)
                item.setData(1, i)
                item.setSizeHint(lw.sizeHint())
                self.userList.addItem(item)
                self.userList.setItemWidget(item, lw)
                lw.clicked.connect(self.showChatRoom)
                self.ChatRooms[i] = GChat(self.user, i, self.Client)
        self.currentUsers = self.onlineUsers
        for i in range(1, self.userList.count()):
            item = self.userList.item(i)
            if item:
                user = item.data(1)
            else:
                continue
            if user not in self.currentUsers and user != "%all%":
                self.userList.takeItem(i)
                del self.ChatRooms[user]

    def showChatRoom(self):
        user = self.userList.currentItem().data(1)
        if user:
            self.currentChatRoom.setVisible(False)
            self.currentChatRoom: GChat = self.ChatRooms[user]
            self.spliter.addWidget(self.currentChatRoom)
            self.currentChatRoom.setVisible(True)
            if user == "%all%":
                self.setWindowTitle(f"ShikiChatRoom-{self.user}" + '-->' + "公共聊天室")
            else:
                self.setWindowTitle(f"ShikiChatRoom-{self.user}" + '-->' + user)
            if self.currentChatRoom.messageList.verticalScrollBar().maximum() != 0:
                self.currentChatRoom.MAXIMUM = self.currentChatRoom.messageList.verticalScrollBar().maximum()
            self.currentChatRoom.messageList.verticalScrollBar().setRange(0, self.currentChatRoom.MAXIMUM)
            self.currentChatRoom.messageList.verticalScrollBar().setValue(self.currentChatRoom.MAXIMUM)
        else:
            self.currentChatRoom.setVisible(False)
            self.currentChatRoom = self.onshow
            self.spliter.addWidget(self.currentChatRoom)
            self.onshow.setVisible(True)
            self.setWindowTitle(f"ShikiChatRoom-{self.user}")

    def drawMessage(self, info):
        sender, receiver, message, content_type, ChatRoom = info[0], info[1], info[2], info[3].split('/')[0], info[4]
        message = MessageBox(sender, receiver, content_type=content_type, content=message)
        item = QListWidgetItem()
        item.setSizeHint(message.grid.sizeHint())
        self.ChatRooms[ChatRoom].messageList.addItem(item)
        self.ChatRooms[ChatRoom].messageList.setItemWidget(item, message)
        if self.ChatRooms[ChatRoom].messageList.verticalScrollBar().maximum() != 0:
            self.ChatRooms[ChatRoom].MAXIMUM = self.currentChatRoom.messageList.verticalScrollBar().maximum()
        self.ChatRooms[ChatRoom].messageList.verticalScrollBar().setRange(0, self.ChatRooms[ChatRoom].MAXIMUM)
        self.ChatRooms[ChatRoom].messageList.verticalScrollBar().setValue(self.ChatRooms[ChatRoom].MAXIMUM)
        self.ChatRooms[ChatRoom].autoSaveMessage(item)

    def messageNotice(self, info):
        user = info[4]
        for i in range(1, self.userList.count()):
            if self.userList.item(i).data(1) == user:
                self.userList.itemWidget(self.userList.item(i)).putNotice()
                break

    def paintEvent(self, a0) -> None:
        painter = QPainter(self)
        painter.drawPixmap(self.rect(), QPixmap('./Client/texture/bg/bg6.png'))

    def clearOfflinedUser(self, user):
        QMessageBox.information(None, '提示', user + "已下线!", buttons=QMessageBox.Ok)
        for i in range(1, self.userList.count()):
            if self.userList.item(i).data(1) == user:
                del self.ChatRooms[user]
                self.currentUsers.remove(user)
                self.userList.takeItem(i)

    def showConnectionClosed(self):
        if self.Client._closed:
            return
        QMessageBox.warning(self, '断开连接', '与服务器中断连接!\n请重新启动客户端', buttons=QMessageBox.Close)

    def setMyAvatar(self):
        path, flag = QFileDialog.getOpenFileName(self, "选择图片", filter="*.jpg;;*.png;;*.gif;;*.webp;;")
        if path:
            img = Image.open(path)
            img = img.resize((100, 100), Image.ANTIALIAS)
            img = img.convert('RGB')
            img.save(f"./Client/cache/users/{self.user}/avatar/MyAvatar.jpg")
            self.avatar.setPixmap(QPixmap(self.avatarPath))
            self.avatar.show()
            self.uploadInfo()

    def uploadInfo(self):
        avatar = f"./Client/cache/users/{self.user}/avatar/MyAvatar.jpg"
        if not os.path.exists(avatar):
            return
        else:
            avatar = open(avatar, 'rb').read()
        headers = {"code": 0, "type": "updateInfo", "sender": self.user,
                   "content-length": len(avatar),
                   "md5": hashlib.md5(avatar).hexdigest()}
        headers = json.dumps(headers, ensure_ascii=False).encode('utf-8-sig')
        self.Client.send(struct.pack('i', len(headers)))
        self.Client.send(headers)
        self.Client.send(avatar)

    def showTime(self):
        for i in self.ChatRooms:
            timeTip = QListWidgetItem(self.getTime("HM"))
            timeTip.setTextAlignment(Qt.AlignHCenter)
            self.ChatRooms[i].messageList.addItem(timeTip)

    def updateInfo(self, info):
        try:
            avatar_user = info[0]
            for i in range(self.ChatRooms[avatar_user].messageList.count()):
                item = self.ChatRooms[avatar_user].messageList.item(i)
                if not item.text():
                    widget = self.ChatRooms[avatar_user].messageList.itemWidget(item)
                    if widget.sender == avatar_user:
                        widget.avatar.setPixmap(QPixmap(widget.avatarPath))
            for i in range(self.ChatRooms["%all%"].messageList.count()):
                item = self.ChatRooms[avatar_user].messageList.item(i)
                if not item.text():
                    widget = self.ChatRooms[avatar_user].messageList.itemWidget(item)
                    if widget.sender == avatar_user:
                        widget.avatar.setPixmap(QPixmap(widget.avatarPath))
            for i in range(2,self.userList.count()):
                item = self.userList.item(i)
                if not item.text():
                    widget = self.userList.itemWidget(item)
                    if widget.target_user == avatar_user:
                        widget.avatar.setPixmap(QPixmap(widget.avatarPath))
                        break
        finally:
            return


if __name__ == '__main__':
    from PyQt5.QtWidgets import QApplication
    app = QApplication(sys.argv)
    # win = QListWidget()
    # item = QListWidgetItem()
    #
    # a = UserItem("Shiki","Artoria",parentList=win,parentItem=item)
    # item.setSizeHint(a.sizeHint())
    # win.addItem(item)
    # win.setItemWidget(item,a)
    win = ChatBody('Shiki', Client())
    win.Client.login('Shiki', "I-LOVE-SHIKI")
    win.runClient()
    win.show()
    app.exec_()
    sys.exit()
