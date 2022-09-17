import os.path
import sys
from PyQt5.QtWidgets import QWidget, QLabel, QListWidgetItem, QListWidget, QGridLayout
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import pyqtSignal, Qt


class UserItem(QWidget):
    clicked = pyqtSignal()

    class MyLabel(QLabel):
        clicked = pyqtSignal()

        def __init__(self, text):
            super(UserItem.MyLabel, self).__init__(text=text)

        def mousePressEvent(self, ev) -> None:
            self.clicked.emit()

    def __init__(self, user, target_user, parentItem: QListWidgetItem, parentList: QListWidget):
        super(UserItem, self).__init__()
        self.user = user
        self.parentItem = parentItem
        self.parentList = parentList
        self.target_user = target_user
        self.avatarPath = f"./Client/cache/users/{self.user}/_from_{self.target_user}/images/avatar/{self.target_user}.avatar"
        self.setupUI()
        self.setupSignals()

    def setupUI(self):
        # self.resize(200,50)
        if self.target_user == "%all%":
            self.Title = self.MyLabel("公共聊天室")
        else:
            self.Title = self.MyLabel(self.target_user)
        self.Title.setAlignment(Qt.AlignVCenter)
        self.Title.setStyleSheet('background-color:transparent;font:15px "华光粗圆_CNKI"')
        self.messageNotice = self.MyLabel('')
        self.messageNotice.setStyleSheet('color:orange;background-color:transparent;font:15px "华光粗黑_CNKI"')
        self.avatar = self.MyLabel('')
        self.avatar.setScaledContents(True)
        self.avatar.setMaximumSize(45, 45)
        self.avatar.setMinimumSize(45, 45)
        self.avatar.setStyleSheet("border:1px solid rgba(230,230,230,150);border-style:outset")
        self.avatar.setPixmap(QPixmap(self.avatarPath))

        self.grid = QGridLayout(self)
        self.grid.addWidget(self.avatar, 0, 0, 2, 1)
        self.grid.addWidget(self.Title, 0, 1, 1, 1)
        self.grid.addWidget(self.messageNotice, 1, 1, 1, 1)

    def setupSignals(self):
        self.Title.clicked.connect(self.clickParentItem)
        self.avatar.clicked.connect(self.clickParentItem)
        self.messageNotice.clicked.connect(self.clickParentItem)

    def clickParentItem(self):
        self.parentItem.setSelected(True)
        self.parentList.setCurrentItem(self.parentItem)
        self.clicked.emit()
        # print(self.parentItem.isSelected())
        self.takeNotice()

    def putNotice(self):
        self.messageNotice.setText('（有新消息）')

    def takeNotice(self):
        self.messageNotice.setText('')


if __name__ == '__main__':
    from PyQt5.QtWidgets import QApplication

    app = QApplication(sys.argv)
    list = QListWidget()
    list.show()
    a = QListWidgetItem()
    win = UserItem("Artoria", "Artoria", parentItem=a, parentList=list)
    win.show()
    list.addItem(a)
    list.addItem(a)
    a.setSizeHint(win.sizeHint())
    list.setItemWidget(a, win)

    app.exec_()

    print(win.sizeHint())
    sys.exit()
