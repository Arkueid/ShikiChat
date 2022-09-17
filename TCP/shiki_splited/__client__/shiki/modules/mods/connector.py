"""
客户端，服务端父类
"""
import socket
from .utils import UserList


class Connector(socket.socket):

    def __init__(self, ip='localhost', port=8080):
        super(Connector, self).__init__(family=socket.AF_INET, type=socket.SOCK_STREAM)
        self.ip = ip
        self.port = port
        self.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    def work_as_server(self):
        self.bind((self.ip, self.port))
        self.listen(5)

    def work_as_client(self, server: tuple):
        self.connect(server)


class Client(Connector):

    def __init__(self, server: tuple = ('localhost', 8080), ip='localhost', port=8080):
        super(Client, self).__init__()
        self.ip = ip
        self.port = port
        self.server = server
        self.work_as_client(self.server)
        self.KeepChat = True

    def login(self, username: str, password: str):
        self.send('login'.encode())
        reply = self.recv(1024).decode()
        if reply == 'login executed':
            self.send(username.encode())
            reply = self.recv(1024).decode()
            if reply == 'username inputted':
                self.send(password.encode())
                reply = self.recv(1024).decode()
                if reply == "success":
                    #
                    print('Logged in successfully!')
                    return 0
                elif reply == "error WP":
                    #
                    print('Wrong password!')
                    return 1
                elif reply == "error NSU":
                    #
                    print('No such user!')
                    return 2
                elif reply == "error UAL":
                    #
                    print('User already logged in!')
                    return 3

    def register(self, username: str, password: str):
        self.send('register'.encode())
        reply = self.recv(1024).decode()
        if reply == "register executed":
            self.send(username.encode())
            reply = self.recv(1024).decode()
            if reply == "username inputted":
                self.send(password.encode())
                reply = self.recv(1024).decode()
                if reply == "success":
                    #
                    userList = UserList('client')
                    userList.add(username, {"PASSWORD": password, "AUTOFILL": "False", "AVATAR": "None"})
                    userList.save()
                    print("Successfully registered!")
                    return 0
            elif reply == "error UAU":
                #
                print(f'Username "{username}" already used!')
                return


if __name__ == '__main__':
    s = Connector(port=9091)
    s.connect(('localhost', 8080))
    s.close()
