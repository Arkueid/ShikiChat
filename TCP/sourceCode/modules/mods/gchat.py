import json
import sys
import time

from PyQt5.QtWidgets import QApplication, QMessageBox

from modules.mods.chat import Chat
from modules.mods.client import Client
from threading import Thread


class GChat(Chat):

    def __init__(self,user, client:Client):
        super(GChat, self).__init__(user=user)
        self.Client = client

    def receive(self):
        while True:
            x = self.Client.recv(1024).decode()
            if x:
                self.textBrowser.append(x)

    def startReceiver(self):
        t = Thread(target=self.receive,daemon=True)
        t2 = Thread(target=self.sendHeartbeat,daemon=True)
        t.start()
        t2.start()

    def send(self):
        text = self.textEdit.toPlainText()
        if text:
            headers = {"code": 0,"type": "message", "content-type": "text", "content-length": len(text)}
            try:
                self.Client.send(json.dumps(headers,ensure_ascii=False).encode('utf-8-sig'))
                self.Client.send(text.encode())
            except:
                QMessageBox.warning(self, '断开连接', '与服务器中断连接!\n请重新启动客户端', buttons=QMessageBox.Close)
                self.Client.close()
                return 1
            text = f'<u>{self.user}</u> {self.getTime("minute")}<p><strong>'+text+'</strong></p>'
            self.textBrowser.append(text)
            self.textEdit.clear()

    def sendHeartbeat(self):
        while True:
            try:
                text = f'{self.getTime("minute")}'.encode()
                headers = {"code": 0,"type": "heartbeat","content-type":"heartbeat","content-length":len(text)}
                self.Client.send(json.dumps(headers,ensure_ascii=False).encode('utf-8-sig'))
                self.Client.send(text)
                time.sleep(60)
            except:
                QMessageBox.warning(self, '断开连接','与服务器中断连接!\n请重新启动客户端',buttons=QMessageBox.Close)
                self.Client.close()
                break

    def closeEvent(self, a0) -> None:
        if self._closed:
            return
        headers = {"code": 1}
        self.Client.send(json.dumps(headers, ensure_ascii=False).encode('utf-8-sig'))



if __name__ == '__main__':
    app = QApplication(sys.argv)
    chat = GChat('shiki',Client())
    chat.Client.login('Shiki','I-LOVE-SHIKI')
    chat.show()
    chat.startReceiver()
    app.exec_()
    sys.exit()