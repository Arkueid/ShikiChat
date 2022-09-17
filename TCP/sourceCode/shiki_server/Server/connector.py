# 不通过服务器连接
# 类似手机通信
import socket


class Connector(socket.socket):

    def __init__(self, ip='localhost', port=8080):
        super(Connector, self).__init__(family=socket.AF_INET,type=socket.SOCK_STREAM)
        self.ip = ip
        self.port = port

    def work_as_server(self):
        self.bind((self.ip, self.port))
        self.listen(5)

    def work_as_client(self, server: tuple):
        self.connect(server)


if __name__ == '__main__':
    s = Connector(port=9091)
    s.connect(('localhost', 8080))
    s.close()




