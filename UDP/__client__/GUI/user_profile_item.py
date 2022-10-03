import sys
from PySide6.QtWidgets import QWidget, QLabel, QListWidgetItem, QListWidget, QGridLayout, QPushButton
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt
from UDP.__client__.modules.utils import Signals


class CustomLabel(QLabel):
    doubleClicked = Signals.doubleClicked

    def mouseDoubleClickEvent(self, a0) -> None:
        self.doubleClicked.emit()


class UserItem(QWidget):

    def __init__(self, user):
        super(UserItem, self).__init__()
        self.user = user
        self.avatarPath = ''
        self.setupUI()

    def setupUI(self):
        self.Title = QLabel(self.user)
        self.Title.setAlignment(Qt.AlignVCenter)
        self.Title.setStyleSheet('background-color:transparent;font:15px "华光粗圆_CNKI"')
        self.avatar = CustomLabel('')
        self.avatar.setScaledContents(True)
        self.avatar.setMaximumSize(50, 50)
        self.avatar.setMinimumSize(50, 50)
        self.avatar.setStyleSheet("border:1px solid rgba(230,230,230,150);border-style:outset")
        self.avatar.setPixmap(QPixmap(self.avatarPath))
        self.btn_eidt = QPushButton('编辑资料')
        self.setMinimumSize(100, 30)

        self.grid = QGridLayout(self)
        self.grid.addWidget(self.avatar, 0, 0, 2, 1)
        self.grid.addWidget(self.Title, 0, 1, 1, 2)
        self.grid.addWidget(self.btn_eidt, 1, 1, 1, 1)


if __name__ == '__main__':
    from PySide6.QtWidgets import QApplication

    app = QApplication(sys.argv)
    list = QListWidget()
    list.show()
    a = QListWidgetItem()
    win = UserItem("Artoria")
    win2 = UserItem('shiki')
    b = QListWidgetItem()
    list.addItem(a)
    list.addItem(b)
    a.setData(3, 'hi')
    b.setData(3, 'yes')
    a.setSizeHint(win.sizeHint())
    b.setSizeHint(win2.sizeHint())
    list.setItemWidget(a, win)
    list.setItemWidget(b, win2)
    print(list.item)
    app.exec_()
