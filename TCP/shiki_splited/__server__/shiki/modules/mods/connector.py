"""
客户端，服务端父类
"""
import hashlib
import json
import os.path
import socket
import struct
import time
from threading import Thread
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


class Server(Connector):

    def __init__(self, ip='', port=8080):
        super(Server, self).__init__()
        self.ip = ip
        self.port = port
        self.current_users = {}
        self.work_as_server()
        if not os.path.exists('./Server/cache/server/'):
            os.makedirs('./Server/cache/server/')
        if not os.path.exists('./Server/cache/server/UserConfig.ini'):
            f = open('./Server/cache/server/UserConfig.ini', 'w')
            f.close()

    def waitConnection(self):
        while True:
            self.connectionProcessor()

    def run(self):
        self.waitConnection()

    def connectionProcessor(self):
        print('\rconnecting...')
        connection, address = self.accept()
        print(f'\rClient{address} connected!')
        try:
            operation = connection.recv(1024).decode()
        except:
            return 0
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
                        self.current_users[username] = connection
                        # self.connections.append(connection)
                        # t1 = Thread(target=self.sendMessage,args=[connection,username],daemon=True)
                        t2 = Thread(target=self.receiveMessage, args=[connection, username, address], daemon=True)
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
                userList.add(username, {"PASSWORD": password})
                userList.save()
                connection.send('success'.encode())
                print(f'User "{username}" registered!')
            else:
                connection.send('error UAU'.encode())

    def receiveMessage(self, connection: socket.socket, username: str, address: tuple):
        while True:
            try:
                headers_len = struct.unpack('i', connection.recv(4))[0]
                headers = connection.recv(headers_len).decode('utf-8-sig')
            except:
                connection.close()
                del self.current_users[username]
                print(f"User {username} from Client{address} disconnected without headers!")
                break
            print(headers)
            headers = json.loads(headers)
            if headers['code'] == 1:
                print(f"User {username} from Client{address} disconnected with code 1!")
                del self.current_users[username]
                connection.close()
                headers = {"code": 0, "type": "current users", "sender": "server", "content-type": "json",
                           "cu": list(self.current_users.keys())}
                headers = json.dumps(headers, ensure_ascii=False).encode('utf-8-sig')
                headers_len = struct.pack('i', len(headers))
                for i in list(self.current_users.values()):
                    i.send(headers_len)
                    i.send(headers)
                break

            elif headers['type'] == "message":
                if 'text' == headers['content-type']:
                    content_length = headers['content-length']
                    message = b''
                    t = content_length
                    while t != 0:
                        if t < 1024:
                            chunk = connection.recv(t)
                        else:
                            chunk = connection.recv(1024)
                        message += chunk
                        t -= len(chunk)

                    # for i in list(self.current_users):
                    #     if self.current_users[i] != connection:
                    #         headers['target']=i
                    #         headers = json.dumps(headers, ensure_ascii=False).encode('utf-8-sig')
                    #         i.send(struct.pack('i',len(headers)))
                    #         i.send(headers)
                    #         i.send(message)
                    if headers['target'] in self.current_users:
                        target_user = self.current_users[headers['target']]
                        headers = json.dumps(headers, ensure_ascii=False).encode('utf-8-sig')
                        target_user.send(struct.pack('i', len(headers)))
                        target_user.send(headers)
                        target_user.send(message)
                    else:
                        headers = {"code": 0, "type": "offline", "target": headers['target']}
                        headers = json.dumps(headers, ensure_ascii=False).encode('utf-8-sig')
                        connection.send(struct.pack('i', len(headers)))
                        connection.send(headers)
                elif 'image' in headers['content-type']:
                    content_length = headers['content-length']
                    message = b''
                    t = content_length
                    while t != 0:
                        if t < 1024:
                            chunk = connection.recv(t)
                        else:
                            chunk = connection.recv(1024)
                        message += chunk
                        t -= len(chunk)
                    print('md5', hashlib.md5(message).hexdigest() == headers['md5'], end=' ')
                    print('received size: ', len(message), 'target size:', headers['content-length'])
                    # for i in list(self.current_users.values()):
                    #     if i != connection:
                    #         headers = json.dumps(headers, ensure_ascii=False).encode('utf-8-sig')
                    #         i.send(struct.pack('i', len(headers)))
                    #         i.send(headers)
                    #         i.send(message)
                    if headers['target'] in self.current_users:
                        target_user = self.current_users[headers['target']]
                        headers = json.dumps(headers, ensure_ascii=False).encode('utf-8-sig')
                        target_user.send(struct.pack('i', len(headers)))
                        target_user.send(headers)
                        target_user.send(message)
                    else:
                        headers = {"code": 0, "type": "offline", "target": headers['target']}
                        headers = json.dumps(headers, ensure_ascii=False).encode('utf-8-sig')
                        connection.send(struct.pack('i', len(headers)))
                        connection.send(headers)

            elif headers['type'] == "public-message":
                if 'text' == headers['content-type']:
                    content_length = headers['content-length']
                    message = b''
                    t = content_length
                    while t != 0:
                        if t < 1024:
                            chunk = connection.recv(t)
                        else:
                            chunk = connection.recv(1024)
                        message += chunk
                        t -= len(chunk)

                    for i in list(self.current_users):
                        if self.current_users[i] != connection:
                            headers['target'] = i
                            headers_copy = json.dumps(headers, ensure_ascii=False).encode('utf-8-sig')
                            self.current_users[i].send(struct.pack('i', len(headers_copy)))
                            self.current_users[i].send(headers_copy)
                            self.current_users[i].send(message)
                    # if headers['target'] in self.current_users:
                    #     target_user = self.current_users[headers['target']]
                    #     headers = json.dumps(headers, ensure_ascii=False).encode('utf-8-sig')
                    #     target_user.send(struct.pack('i', len(headers)))
                    #     target_user.send(headers)
                    #     target_user.send(message)
                    # else:
                    #     headers = {"code": 0, "type": "offline", "target": headers['target']}
                    #     headers = json.dumps(headers, ensure_ascii=False).encode('utf-8-sig')
                    #     connection.send(struct.pack('i', len(headers)))
                    #     connection.send(headers)
                elif 'image' in headers['content-type']:
                    content_length = headers['content-length']
                    message = b''
                    t = content_length
                    while t != 0:
                        if t < 1024:
                            chunk = connection.recv(t)
                        else:
                            chunk = connection.recv(1024)
                        message += chunk
                        t -= len(chunk)
                    print('md5', hashlib.md5(message).hexdigest() == headers['md5'], end=' ')
                    print('received size: ', len(message), 'target size:', headers['content-length'])
                    for i in list(self.current_users.values()):
                        if i != connection:
                            headers_copy = json.dumps(headers, ensure_ascii=False).encode('utf-8-sig')
                            i.send(struct.pack('i', len(headers_copy)))
                            i.send(headers_copy)
                            i.send(message)
                    # if headers['target'] in self.current_users:
                    #     target_user = self.current_users[headers['target']]
                    #     headers = json.dumps(headers, ensure_ascii=False).encode('utf-8-sig')
                    #     target_user.send(struct.pack('i', len(headers)))
                    #     target_user.send(headers)
                    #     target_user.send(message)
                    # else:
                    #     headers = {"code":0, "type": "offline","target": headers['target']}
                    #     headers = json.dumps(headers, ensure_ascii=False).encode('utf-8-sig')
                    #     connection.send(struct.pack('i', len(headers)))
                    #     connection.send(headers)

            elif headers['type'] == "heartbeat":
                content_length = headers['content-length']
                message = ''
                t = content_length
                while t != 0:
                    if t < 1024:
                        message += connection.recv(t).decode()
                        t = 0
                    else:
                        message += connection.recv(1024).decode()
                        t -= 1024
                headers = {"code": 0, "type": "current users", "content-type": "list",
                           "cu": list(self.current_users.keys()) + ["%all%"]}
                headers = json.dumps(headers, ensure_ascii=False).encode('utf-8-sig')
                headers_len = struct.pack('i', len(headers))
                for i in list(self.current_users.values()):
                    i.send(headers_len)
                    i.send(headers)

            elif headers['type'] == "RFA":
                path = f'./Server/cache/users/{headers["avatar-user"]}/profile.avatar'
                if os.path.exists(path):
                    with open(path, 'rb') as f:
                        img = f.read()
                    headers = {"code": 0, "type": "avatar", "content-type": "image/.avatar", "content-length": len(img),
                               "target": headers["sender"], "avatar-user": headers["avatar-user"],
                               "sender": "server", "md5": hashlib.md5(img).hexdigest()}
                    headers = json.dumps(headers, ensure_ascii=False).encode('utf-8-sig')
                    connection.send(struct.pack('i', len(headers)))
                    connection.send(headers)
                    connection.send(img)

            elif headers['type'] == "updateInfo":
                content_length = headers['content-length']
                message = b''
                t = content_length
                if not os.path.exists(f"./Server/cache/users/{headers['sender']}"):
                    os.mkdir(f"./Server/cache/users/{headers['sender']}")
                with open(f"./Server/cache/users/{headers['sender']}/profile.avatar", 'wb') as f:
                    while t != 0:
                        if t < 1024:
                            chunk = connection.recv(t)
                        else:
                            chunk = connection.recv(1024)
                        message += chunk
                        f.write(chunk)
                        t -= len(chunk)
                print('md5', hashlib.md5(message).hexdigest() == headers['md5'], end=' ')
                print('received size: ', len(message), 'target size:', headers['content-length'])
                path = f'./Server/cache/users/{headers["sender"]}/profile.avatar'
                if os.path.exists(path):
                    with open(path, 'rb') as f:
                        img = f.read()
                headers = {"code": 0, "type": "avatar", "content-type": "image/.avatar",
                           "content-length": len(img),
                           "target": None, "avatar-user": headers["sender"],
                           "sender": "server", "md5": hashlib.md5(img).hexdigest()}
                for i in self.current_users:
                    user = self.current_users[i]
                    headers['target'] = i
                    headers_copy = json.dumps(headers, ensure_ascii=False).encode('utf-8-sig')
                    user.send(struct.pack('i', len(headers_copy)))
                    user.send(headers_copy)
                    user.send(img)

    def getTime(self, by):
        if by == 'day':
            return time.strftime('%Y-%m-%d', time.localtime(int(time.time())))
        if by == 'minute':
            return time.strftime('%Y-%m-%d %H:%M', time.localtime(int(time.time())))


if __name__ == '__main__':
    s = Connector(port=9091)
    s.connect(('localhost', 8080))
    s.close()
