import sys
from PyQt5.QtWidgets import QFrame, QApplication, QLabel, QWidget, QLineEdit, QPushButton, QGridLayout, QCheckBox, \
    QCompleter
from PyQt5.QtGui import QPixmap, QPainter, QIcon


class RegisterPage(QFrame):

    def __init__(self):
        super(RegisterPage, self).__init__()
        self.setupUI()

    def setupUI(self):
        self.setMaximumWidth(370)
        self.setMaximumHeight(220)
        self.setMinimumSize(340,220)

        self.label_username = QLabel("用户名")
        self.label_username.setMinimumSize(50,40)
        self.label_password = QLabel("密码  ")
        self.label_password.setMinimumSize(50,40)
        self.label_check_password = QLabel("确认密码")
        self.label_check_password.setMinimumSize(50, 40)
        self.button_register = QPushButton("注册")
        self.button_register.setMinimumSize(100, 40)
        self.button_back = QPushButton("返回")
        self.button_back.setMinimumSize(100, 40)
        self.lineEdit_username = QLineEdit()
        self.lineEdit_username.setMinimumSize(120,30)
        self.lineEdit_password = QLineEdit()
        self.lineEdit_password.setMinimumSize(120,30)
        self.lineEdit_password.setEchoMode(self.lineEdit_password.Password)
        self.lineEdit_check_password = QLineEdit()
        self.lineEdit_check_password.setMinimumSize(120, 30)
        self.lineEdit_check_password.setEchoMode(self.lineEdit_password.Password)
        self.grid_main = QGridLayout(self)
        self.grid_main.addWidget(self.label_username,0,0,1,1)
        self.grid_main.addWidget(self.label_password,1,0,1,1)
        self.grid_main.addWidget(self.label_check_password, 2, 0, 1, 1)
        self.grid_main.addWidget(self.lineEdit_username,0,2,1,4)
        self.grid_main.addWidget(self.lineEdit_password,1,2,1,4)
        self.grid_main.addWidget(self.lineEdit_check_password,2,2,1,4)
        self.grid_main.addWidget(self.button_register, 3, 2, 1, 3)
        self.grid_main.addWidget(self.button_back, 4, 2, 1, 3)


class LoginPage(QFrame):

    def __init__(self):
        super(LoginPage, self).__init__()
        self.setupUI()

    def setupUI(self):
        self.setMaximumWidth(370)
        self.setMaximumHeight(220)
        self.setMinimumSize(340, 220)

        self.label_username = QLabel("用户名")
        self.label_username.setMinimumSize(50, 40)
        self.label_password = QLabel("密码  ")
        self.label_password.setMinimumSize(50, 40)
        self.button_login = QPushButton("登录")
        self.button_login.setMinimumSize(100, 40)
        self.button_register = QPushButton("注册")
        self.button_register.setMinimumSize(100, 40)
        self.lineEdit_username = QLineEdit()
        self.lineEdit_username.setClearButtonEnabled(True)
        self.lineEdit_username.setMinimumSize(120, 30)
        self.lineEdit_password = QLineEdit()
        self.lineEdit_password.setMinimumSize(120, 30)
        self.lineEdit_password.setClearButtonEnabled(True)
        self.lineEdit_password.setEchoMode(self.lineEdit_password.Password)
        self.checkbox = QCheckBox('记住密码')
        self.btn_ConnectionSettings = QPushButton('连接配置')
        self.grid_main = QGridLayout(self)
        self.grid_main.addWidget(self.label_username, 0, 0, 1, 1)
        self.grid_main.addWidget(self.label_password, 1, 0, 1, 1)
        self.grid_main.addWidget(self.lineEdit_username, 0, 2, 1, 4)
        self.grid_main.addWidget(self.lineEdit_password, 1, 2, 1, 4)
        self.grid_main.addWidget(self.checkbox, 2,2,1,2)
        self.grid_main.addWidget(self.btn_ConnectionSettings,2,4,1,2)
        self.grid_main.addWidget(self.button_login, 3, 2, 1, 3)
        self.grid_main.addWidget(self.button_register, 4, 2, 1, 3)


class Entrance(QWidget):

    def __init__(self):
        super(Entrance, self).__init__()
        self.Login = LoginPage()
        self.Register = RegisterPage()
        self.setupUI()

    def setupUI(self):
        self.setWindowTitle('Shiki-登录')
        self.setMaximumWidth(370)
        self.setMaximumHeight(220)
        self.setMinimumSize(340, 220)
        self.setWindowIcon(QIcon('.\\texture\\icon\\ShikiSan.png'))

        self.Login.setParent(self)
        self.Register.setParent(self)
        self.Login.button_register.clicked.connect(self.Login_onClickRegister)
        self.Register.button_back.clicked.connect(self.Register_onClickBack)
        self.Register.setVisible(False)

    def Login_onClickRegister(self):
        self.setWindowTitle('Shiki-注册')
        self.Login.setVisible(False)
        self.Register.setVisible(True)

    def Register_onClickBack(self):
        self.setWindowTitle('Shiki-登录')
        self.Register.setVisible(False)
        self.Login.setVisible(True)

    def paintEvent(self, a0) -> None:
        painter = QPainter(self)
        painter.drawPixmap(self.rect(), QPixmap('.\\texture\\bg\\entrance_bg.jpg'))


if __name__ == '__main__':
    app = QApplication(sys.argv)

    win = Entrance()
    win.show()

    sys.exit(app.exec_())
