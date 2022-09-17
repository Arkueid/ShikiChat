from modules.mods.client import Client
from modules.GUI.entrance import Entrance
from PyQt5.QtWidgets import QMessageBox, QShortcut, QInputDialog, QCompleter
from modules.mods.utils import UserList
from modules.mods.gchat import GChat


class Hi(Entrance):

    def __init__(self):
        super(Hi, self).__init__()
        self.ip = 'localhost'
        self.port = 8080
        self.Users = UserList('client')
        self.setupSignals()

    def setupSignals(self):
        self.Register.button_register.clicked.connect(self.register)
        self.Login.button_login.clicked.connect(self.login)
        QShortcut(16777220,self.Login,self.Login.button_login.click)
        QShortcut(16777220,self.Register,self.Register.button_register.click)
        self.Login.lineEdit_username.textChanged.connect(self.isAutoFill)
        self.Login.btn_ConnectionSettings.clicked.connect(self.setConnection)
        self.Login.lineEdit_username.setCompleter(QCompleter(self.Users))

    def register(self):
        username = self.Register.lineEdit_username.text()
        password = self.Register.lineEdit_password.text()
        check_password = self.Register.lineEdit_check_password.text()
        if username:
            if password:
                if check_password:
                    if password == check_password:
                        try:
                            self.Client = Client((self.ip,self.port))
                            if self.Client.register(username,password,check_password) == 0:
                                QMessageBox.information(self, '注册成功', f'注册成功! 用户名为: {username}',buttons=QMessageBox.Yes)
                                self.Register.lineEdit_username.clear()
                                self.Register.lineEdit_password.clear()
                                self.Register.lineEdit_check_password.clear()
                                self.Register.button_back.click()
                                self.Users.update()
                            else:
                                QMessageBox.information(self, '注册失败', '用户名已注册! ', buttons=QMessageBox.Ignore)
                                self.Register.lineEdit_username.clear()
                                self.Register.lineEdit_password.clear()
                                self.Register.lineEdit_check_password.clear()
                            self.Client.close()
                        except ConnectionRefusedError as e:
                            QMessageBox.warning(self, '注册失败', '无法连接到服务器!', buttons=QMessageBox.Ignore)
                    else:
                        QMessageBox.information(self, '注册失败', '两次密码不一致! ', buttons=QMessageBox.Ignore)
                        self.Register.lineEdit_password.clear()
                        self.Register.lineEdit_check_password.clear()
                else:
                    QMessageBox.information(self,'提示','请确认密码! ',buttons=QMessageBox.Ignore)
            else:
                QMessageBox.information(self, '提示', '请输入密码! ', buttons=QMessageBox.Ignore)
        else:
            QMessageBox.information(self, '提示', '请输入用户名! ', buttons=QMessageBox.Ignore)


    def login(self):
        username = self.Login.lineEdit_username.text()
        if username:
            password = self.Login.lineEdit_password.text()
            if password:
                try:
                    self.Client = Client((self.ip, self.port))
                    reply = self.Client.login(username,password)
                    if reply == 0:
                            self.GChat = GChat(username,self.Client)
                            QMessageBox.information(self,'登录成功', f'{username},欢迎回来~',buttons=QMessageBox.Yes)
                            self.close()
                            self.GChat.startReceiver()
                            self.GChat.setWindowTitle(f'Shiki-ChatRoom-{username}')
                            self.GChat.show()
                            self.Users[username]['AUTOFILL'] = str(self.Login.checkbox.isChecked())
                            self.Users.save()
                            self.Users.update()
                            self.Login.lineEdit_password.clear()
                    elif reply == 1:
                        QMessageBox.information(self,'登录失败','密码错误! ',buttons=QMessageBox.Ignore)
                        self.Login.lineEdit_password.clear()
                    elif reply == 2:
                        QMessageBox.information(self, '登录失败','用户名不存在! ',buttons=QMessageBox.Ignore)
                        self.Login.lineEdit_password.clear()
                        self.Login.lineEdit_username.clear()
                    elif reply == 3:
                        QMessageBox.warning(self, '登录失败', '该用户已登录!', buttons=QMessageBox.Ignore)
                except ConnectionRefusedError as e:
                    QMessageBox.warning(self, '登录失败', '无法连接到服务器!', buttons=QMessageBox.Ignore)
            else:
                QMessageBox.information(self, '提示','请输入密码! ', buttons=QMessageBox.Ignore)
        else:
            QMessageBox.information(self, '提示', '请输入用户名! ',buttons=QMessageBox.Ignore)

    def isAutoFill(self):
        if self.Login.lineEdit_username.text() in self.Users:
            if self.Users.get(self.Login.lineEdit_username.text(), "AUTOFILL") == "True":
                self.Login.lineEdit_password.setText(self.Users.get(self.Login.lineEdit_username.text(),"PASSWORD"))
                self.Login.checkbox.setChecked(True)
        else:
            self.Login.lineEdit_password.clear()
            self.Login.checkbox.setChecked(False)

    def setConnection(self):
        text, flag = QInputDialog.getItem(self,'连接配置','服务器IP及端口，示例: 255.255.255.255:8080',['localhost:8080','X.tcp.ngrok.io:XXXX'])
        if flag:
            try:
                self.ip, self.port = text.split(':')
                self.port = int(self.port)
            except:
                QMessageBox.warning(self, '错误','服务器配置有误')