import sys

from PySide6.QtWidgets import QListWidgetItem, QListWidget, QApplication


if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = QListWidget()
    for i in range(100):
        item = QListWidgetItem()
        item.setText(str(i))
        item.setData(5, (i, (i+1000, i+999)))
        win.addItem(item)
    win.show()
    for i in range(win.count()):
        item = win.item(i)
        print(item.data(5))
    sys.exit(app.exec_())
