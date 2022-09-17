import sys
import datetime
import time
from PyQt5.QtCore import Qt, QRegExp, QDateTime
from PyQt5.QtWidgets import QWidget, QApplication, QGridLayout, QLineEdit, QPushButton, QLabel, QTextEdit, QDateEdit, QDateTimeEdit
from PyQt5.QtGui import QPixmap, QRegExpValidator


class InfoPage(QWidget):

    def __init__(self, profile, avatar):
        super(InfoPage, self).__init__()
        self.setupUI()
        self.load_profile_from(profile, avatar)
        self.setupSignals()

    def load_profile_from(self, profile, avatar):
        uid, username, register_date, birthday, age, brief_intro = profile
        self.user_name = username
        self.uid = uid
        self.register_date = datetime.datetime(*list(time.strptime(register_date, "%Y-%m-%d %H:%M:%S"))[:5])
        self.birthday = datetime.datetime(*list(time.strptime(birthday, "%Y-%m-%d %H:%M:%S"))[:5])
        self.age = str(age)
        self.brief_introduction = brief_intro
        self.avatar = avatar

        self.setWindowTitle(self.uid + "资料卡")
        self.lbl_avatar.setPixmap(QPixmap(self.avatar))
        self.ldt_username.setText(self.user_name)
        self.ldt_username.setToolTip(self.user_name)
        self.ldt_uid.setText(self.uid)
        self.ldt_register_date.setDateTime(QDateTime(self.register_date))
        self.ldt_age.setText(self.age)
        self.ldt_birthday.setDateTime(QDateTime(self.birthday))
        self.ldt_brief_introduction.setText(self.brief_introduction)

    def setupSignals(self):
        self.btn_edit.clicked.connect(self.to_edit_mode)
        self.btn_confirm.clicked.connect(self.disable_edit_mode)
        self.btn_cancel.clicked.connect(self.disable_edit_mode)
        self.btn_close.clicked.connect(self.close)

    def setupUI(self):
        self.resize(350, 500)
        self.grid = QGridLayout(self)

        self.lbl_avatar = QLabel()
        self.lbl_avatar.setScaledContents(True)
        self.lbl_avatar.setMaximumSize(70, 70)
        self.lbl_username = QLabel('昵称')
        self.ldt_username = QLineEdit()
        self.ldt_username.setMinimumHeight(35)
        self.lbl_uid = QLabel('UID')
        self.ldt_uid = QLineEdit()
        self.ldt_uid.setMinimumHeight(35)
        self.lbl_register_date = QLabel('注册日期')
        self.ldt_register_date = QDateTimeEdit()
        self.ldt_register_date.setMinimumHeight(35)
        self.lbl_age = QLabel('年龄')
        self.ldt_age = QLineEdit()
        # self.ldt_age = QLineEdit()
        self.ldt_age.setValidator(QRegExpValidator(QRegExp(r'^[^0][0-9]{0,2}')))
        self.ldt_age.setMinimumHeight(35)
        self.lbl_birthday = QLabel('生日')
        self.ldt_birthday = QDateEdit()
        self.ldt_birthday.setMinimumHeight(35)
        self.lbl_brief_introduction = QLabel('简介')
        self.lbl_brief_introduction.setMinimumHeight(35)
        self.ldt_brief_introduction = QTextEdit()
        self.ldt_brief_introduction.setAlignment(Qt.AlignTop|Qt.AlignLeft)
        self.btn_edit = QPushButton('编辑')
        self.btn_close = QPushButton('关闭')
        self.btn_confirm = QPushButton('确认')
        self.btn_cancel = QPushButton('取消')

        self.grid.addWidget(self.lbl_avatar, 0, 0, 2, 1)
        self.grid.addWidget(self.lbl_username, 0, 1, 1, 1)
        self.grid.addWidget(self.ldt_username, 0, 2, 1, 2)
        self.grid.addWidget(self.lbl_uid, 1, 1, 1, 1)
        self.grid.addWidget(self.ldt_uid, 1, 2, 1, 2)
        self.grid.addWidget(self.lbl_register_date, 3, 0, 1, 1)
        self.grid.addWidget(self.ldt_register_date, 3, 1, 1, 2)
        self.grid.addWidget(self.lbl_birthday, 4, 0, 1, 2)
        self.grid.addWidget(self.ldt_birthday, 4, 1, 1, 2)
        self.grid.addWidget(self.lbl_age, 5, 0, 1, 1)
        self.grid.addWidget(self.ldt_age, 5, 1, 1, 1)
        self.grid.addWidget(self.lbl_brief_introduction, 6, 0, 1, 1)
        self.grid.addWidget(self.ldt_brief_introduction, 7, 0, 1, 4)
        self.grid.addWidget(self.btn_edit, 8, 0, 1, 2)
        self.grid.addWidget(self.btn_close, 8, 3, 1, 2)
        self.grid.addWidget(self.btn_confirm, 8, 0, 1, 2)
        self.grid.addWidget(self.btn_cancel, 8, 3, 1, 2)
        self.disable_edit_mode()
    
    def to_edit_mode(self):
        self.ldt_brief_introduction.setEnabled(True)
        self.ldt_birthday.setEnabled(True)
        self.ldt_username.setEnabled(True)
        self.ldt_age.setEnabled(True)
        self.btn_confirm.setVisible(True)
        self.btn_cancel.setVisible(True)
        self.btn_edit.setVisible(False)
        self.btn_close.setVisible(False)

    def setSelf(self, a0: bool):
        if not a0:
            self.btn_edit.setVisible(False)

    def disable_edit_mode(self):
        self.ldt_brief_introduction.setEnabled(False)
        self.ldt_birthday.setEnabled(False)
        self.ldt_username.setEnabled(False)
        self.ldt_register_date.setEnabled(False)
        self.ldt_age.setEnabled(False)
        self.ldt_uid.setEnabled(False)
        self.btn_confirm.setVisible(False)
        self.btn_cancel.setVisible(False)
        self.btn_edit.setVisible(True)
        self.btn_close.setVisible(True)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    profile = 'Ass123', 'Ass123', '2022-6-22 9:30:40', '2001-11-10 00:00:00', '20', 'no intro'
    win = InfoPage(profile, r'C:\Users\ArcueidBrunestud\Desktop\ShikiChat\UDP\__client__\wallhaven-ym8yod.png')
    win.show()
    sys.exit(app.exec_())