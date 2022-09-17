import json
import socket
import time

from modules.mods.connector import Connector
from threading import Thread
from modules.mods.utils import UserList


class Server(Connector):

    def __init__(self, ip='localhost', port=8080):
        super(Server, self).__init__()
        self.ip = ip
        self.port = port
        self.connections = []
        self.current_users = []
        self.work_as_server()

    def waitConnection(self):
        while True:
            self.connectionProcessor()

    def run(self):
        t = Thread(target=self.waitConnection, daemon=True)
        t.start()
        while True:
            pass

    def connectionProcessor(self):
        print('\rconnecting...')
        connection, address = self.accept()
        connection.setsockopt(socket.SOL_SOCKET,socket.SO_KEEPALIVE, True)
        connection.ioctl(socket.SIO_KEEPALIVE_VALS,
                         (1,60*1000,30*1000))
        print(f'\rClient{address} connected!')
        operation = connection.recv(1024).decode()
        if operation == "login":
            connection.send('login executed'.encode())
            username = connection.recv(1024).decode()
            connection.send('username inputted'.encode())
            password = connection.recv(1024).decode()
            userList = UserList('server')
            if username in userList:
                if username not in self.current_users:
                    if password == userList.get(username, "PASSWORD"):
                        connection.send('success'.encode())
                        print(f'User: {username} logged in!')
                        self.current_users.append(username)
                        self.connections.append(connection)
                        # t1 = Thread(target=self.sendMessage,args=[connection,username],daemon=True)
                        t2 = Thread(target=self.receiveMessage, args=[connection,username,address],daemon=True)
                        # t1.start()
                        t2.start()
                    else:
                        connection.send('error WP'.encode())
                else:
                    connection.send('error UAL'.encode())
            else:
                connection.send('error NSU'.encode())
        elif operation == "register":
            connection.send('register executed'.encode())
            username = connection.recv(1024).decode()
            userList = UserList('server')
            if username not in userList:
                connection.send('username inputted'.encode())
                password = connection.recv(1024).decode()
                userList.add(username,{"PASSWORD":password})
                userList.save()
                connection.send('success'.encode())
                print(f'User "{username}" registered!')
            else:
                connection.send('error UAU'.encode())

    # def sendMessage(self, connection:socket.socket, username):
    #     while True:
    #         x = input(f'>>>{username}: ')
    #         connection.send(('<u>Server</u><br>'+x+'<br>').encode())

    def receiveMessage(self, connection: socket.socket,username: str,address: tuple):
        while True:
            headers = connection.recv(1024).decode('utf-8-sig')
            connection.send(''.encode())
            # print(headers)
            headers = json.loads(headers)
            if headers['code'] == 1:
                print(f"User {username} from Client{address} disconnected!")
                self.current_users.remove(username)
                self.connections.remove(connection)
                break
            # print(headers)
            # print(content_length)
            content_length = headers['content-length']//1024 + 1
            message = ''
            for i in range(content_length):
                message += connection.recv(1024).decode()
            if headers['type'] == "message":
                for i in self.connections:
                    if i != connection:
                        i.send((f'<u>{username}</u> {self.getTime("minute")}<p><strong>'+message+'</strong></p>').encode())
                print(f'\r{username}: {message}')
            elif headers['type'] == "heartbeat":
                print(f'\rheartbeat from Client{address}')



    def getTime(self,by):
        if by == 'day':
            return time.strftime('%Y-%m-%d', time.localtime(int(time.time())))
        if by == 'minute':
            return time.strftime('%Y/%m/%d %H:%M', time.localtime(int(time.time())))


if __name__ == '__main__':
    s = Server()
    s.run()