import sys
from PyQt5.QtWidgets import QApplication
from modules.mods.hi import Hi as Shiki

if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = Shiki()
    win.show()
    sys.exit(app.exec_())
