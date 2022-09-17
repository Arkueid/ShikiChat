from .modules.mods import Hi
from PyQt5.QtWidgets import QApplication
from sys import argv, exit
from .modules.mods import Server


class Shiki(Hi):
    app = QApplication(argv)

    def __init__(self):
        super(Shiki, self).__init__()

    def run(self):
        self.show()
        exit(self.app.exec_())


__all__ = ["Shiki", "Server"]

