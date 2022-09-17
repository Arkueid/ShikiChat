from modules.mods.connector import Connector
from modules.mods.utils import UserList


class Client(Connector):

    def __init__(self,server: tuple=('localhost',8080),ip='localhost', port=8080):
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
                        print('Login successfully!')
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

    def register(self, username: str, password: str, check_password: str):
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
                    userList.add(username,{"PASSWORD":password,"AUTOFILL":False})
                    userList.save()
                    print("Successfully registered!")
                    return 0
            elif reply == "error UAU":
                #
                print(f'Username "{username}" already used!')
                return


if __name__ == '__main__':
    c = Client(port=9090)
    c.login('Shiki',"I-LOVE-SHIKI")
    # c.register('Shiki1','123456','123456')

