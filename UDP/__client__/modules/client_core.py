import hashlib
import json
import os.path
import re
import socket
import base64
import struct
from .utils import get_curr_time


class ClientCore:

    def __init__(self, send_core_addr=('localhost', 8091), recv_core_addr=('localhost', 8092)):
        # 设置发送核心类型为UDP
        self.send_core = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # 允许发送核心重用本地地址和端口，避免bind失败
        self.send_core.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # 发送核心的ip端口
        self.send_core_addr = send_core_addr
        # 绑定发送核心ip端口
        self.send_core.bind(self.send_core_addr)
        # 设置接收核心类型为UDP
        self.recv_core = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # 允许接收核心重用本地地址和端口，避免bind失败
        self.recv_core.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # 接收核心的ip与端口
        self.recv_core_addr = recv_core_addr
        # 接收核心绑定ip与端口
        self.recv_core.bind(self.recv_core_addr)
        self.account_id: str = ''
        self.curr_users: dict = dict()
        self.new_online_users: dict = dict()
        self.new_offline_users: dict = dict()

    def login(self, account_id, password, server_addr):
        """
        客户端登录操作
        :param account_id: 登录账号
        :param password: 登录密码
        :param server_addr: 服务端地址，元组(ip, port)
        :return:
        """
        self.account_id = account_id
        headers = {
            "code": 0,
            "type": "login",
            "account": base64.b64encode(account_id.encode()).decode(),
            "password": hashlib.md5(password.encode()).hexdigest(),
            "addr": self.recv_core_addr,
            "ct": get_curr_time()
        }
        self.sendto(headers, server_addr)

    def register(self, account_id, password, server_addr):
        """
        客户端注册
        :param account_id: 登录账号
        :param password: 登录密码
        :param server_addr: 服务端地址，元组(ip, port)
        :return:
        """
        if 6 <= len(account_id) <= 30:
            # 判断账号是否合法
            if not re.findall(r"\W", account_id) and re.findall("[a-z]+", account_id) and re.findall("[A-Z]+", account_id) and re.findall(r"\d+", account_id):
                # 判断密码长度
                if 6 <= len(password) <= 16:
                    # 判断密码是否只包含数字，大小写字母，下划线
                    if not re.findall(r"\W", password) and re.findall("[a-z]+", password) and re.findall("[A-Z]+", password) and re.findall(r"\d+", password):
                        headers = {
                            "code": 0,
                            "type": "register",
                            "sender": "client",
                            "account": base64.b64encode(account_id.encode()).decode(),
                            "password": base64.b64encode(password.encode()).decode(),
                            "addr": self.recv_core_addr,
                            "ct": get_curr_time()
                        }
                        self.sendto(headers, server_addr)
                        return 0
                    else:
                        print("ClientCore.register:\n", "密码必须包含数字、大小写字母，不包含下划线以外的特殊字符!")
                        return 1
                else:
                    print("ClientCore.register:\n", "密码长度应为6-16位!")
                    return 2
            else:
                print("ClientCore.register:\n", "账号必须包含数字、大小写字母，不包含下划线以外的特殊字符!")
                return 3
        else:
            print("ClientCore.register:\n", "账号长度应为6-16位!")
            return 4

    def sendto(self, headers, addr):
        """
        常用发送代码串，避免重复
        :param headers: 要发送的数据报
        :param addr: 目标地址，元组(ip, port)
        :return:
        """
        # 数据报头
        headers = json.dumps(headers).encode()
        # 数据报头长度，压缩为4位长度
        headers_len = struct.pack('i', len(headers))
        # 依次发送数据报头长度，数据报
        self.send_core.sendto(headers_len, addr)
        self.send_core.sendto(headers, addr)

    def recv_from(self):
        """
        常用接收代码串，避免重复
        :return: 接收到的数据报headers(字典)和发送者的地址addr(元组)
        """
        # 接收数据报长度
        headers_len, addr = self.recv_core.recvfrom(4)
        headers_len = struct.unpack('i', headers_len)[0]
        # 接收数据报
        headers, addr = self.recv_core.recvfrom(headers_len)
        headers = json.loads(headers.decode())
        return headers, addr

    def signOut(self, server_addr):
        """发送离线数据报，告知服务端用户下线"""
        headers = {
            "code": 0,
            "type": "SignOut",
            "sender": base64.b64encode(self.account_id.encode()).decode(),
            "ct": get_curr_time()
        }
        self.sendto(headers, server_addr)

    def send_content_to(self, text=None, text_file=None, byte_file=None, addr=None, add: dict = None):
        """发送数据报以外的各种数据，包括文本，文本文件，二进制文件"""
        # 发送文本
        if text and not text_file and not byte_file:
            content = text.encode()
            headers = {
                "code": 0,
                "type": "message",
                "sender": base64.b64encode(self.account_id.encode()).decode(),
                "receiver": None,
                "content-type": "text",
                "content-length": len(content),
                "md5": hashlib.md5(content).hexdigest(),
                "ct": get_curr_time()
            }
        # 发送文本文件
        elif text_file and not text and not byte_file:
            content = open(text_file, 'r', encoding='utf-8').read().encode()
            headers = {
                "code": 0,
                "type": "message",
                "sender": base64.b64encode(self.account_id.encode()).decode(),
                "receiver": None,
                "content-type": "text-file/" + os.path.splitext(os.path.basename(text_file))[-1],
                "content-length": len(content),
                "md5": hashlib.md5(content).hexdigest(),
                "ct": get_curr_time()
            }
        # 发送二进制文件
        elif byte_file and not text and not text_file:
            content = open(byte_file, 'rb').read()
            headers = {
                "code": 0,
                "type": "message",
                "sender": base64.b64encode(self.account_id.encode()).decode(),
                "receiver": None,
                "content-type": "byte-file/" + os.path.splitext(os.path.basename(byte_file))[-1],
                "content-length": len(content),
                "md5": hashlib.md5(content).hexdigest(),
                "ct": get_curr_time()
            }
        else:
            # 其他情况终止发送
            return
        if add:
            for i in add:
                headers[i] = add[i]
        self.sendto(headers, addr)
        # 已发送数据大小
        send_content_length = 0
        # 要发送的数据总大小
        content_length = len(content)
        # 数据指针，每次读取并发送1024长度，发送完指针往后移动1024位
        ptr = 0
        while send_content_length < content_length:
            # 剩余数据大小
            left = content_length - send_content_length
            if left < 40960:
                # 剩余数据小于1024，则按剩余数据大小读取
                a = self.send_core.sendto(content[ptr:ptr + left], addr)
                ptr += left
                send_content_length += left
            else:
                # 剩余数据大于1024时，按1024长度读取
                self.send_core.sendto(content[ptr:ptr + 40960], addr)
                ptr += 40960
                send_content_length += 40960
            self.send_core.recvfrom(2)
            # 打印发送进度
            # print('\r', send_content_length, content_length, end='')
        # print()

    def handle_content(self, headers, addr, save_path=''):
        """处理接收数据报以外的数据"""
        # 接收数据
        # 判断数据是否为文件
        if 'file' in headers['content-type']:
            # 合成文件路径
            file_name = os.path.join(save_path, f"{headers['md5']}{headers['content-type'].split('/')[-1]}")
            # 检测文件是否存在
            if os.path.exists(file_name):
                with open(file_name, 'w') as f:
                    f.close()
            # 接收文本文件，分批次保存
            if 'text' in headers['content-type']:
                # 文件总长度
                content_length = headers['content-length']
                # 已接收文件长度
                recv_content_length = 0
                while recv_content_length < content_length:
                    chunk = self.recv_core.recv(40960)
                    self.send_core.sendto(b'ok', addr)
                    recv_content_length += len(chunk)
                    with open(file_name, 'a', encoding='utf-8') as f:
                        f.write(chunk.decode())
                    # print('\r', recv_content_length, content_length, end='')
                # print()
                # 判断文件完整性
                # 判断接收的数据md5值是否和数据报中md5值相符
                if headers['md5'] == hashlib.md5(open(file_name, 'rb').read()).hexdigest():
                    return f"{headers['content-type']}",\
                           True,\
                           f"{os.path.getsize(file_name)}/{headers['content-length']}"
                else:
                    return f"\n{headers['content-type']}",\
                           False,\
                           f"{os.path.getsize(file_name)}/{headers['content-length']}"
            else:
                content_length = headers['content-length']
                recv_content_length = 0
                while recv_content_length < content_length:
                    # 读取一个数据包
                    chunk = self.recv_core.recv(40960)
                    # 发送已接收，发送者接收才能继续发送，避免丢包
                    self.send_core.sendto(b'ok', addr)
                    recv_content_length += len(chunk)
                    # 写入切割后的数据片段
                    with open(file_name, 'ab') as f:
                        f.write(chunk)
                    # 打印接收进度
                    # print('\r', recv_content_length, content_length, end='')
                # print()
                # 判断文件完整性
                # 判断接收的数据md5值是否和数据报中md5值相符
                if headers['md5'] == hashlib.md5(open(file_name, 'rb').read()).hexdigest():
                    return f"{headers['content-type']}", \
                           True, \
                           f"{os.path.getsize(file_name)}/{headers['content-length']}"
                else:
                    return f"\n{headers['content-type']}", \
                           False, \
                           f"{os.path.getsize(file_name)}/{headers['content-length']}"
        else:
            content_length = headers['content-length']
            recv_content_length = 0
            recv_content = b''
            while recv_content_length < content_length:
                chunk = self.recv_core.recv(40960)
                self.send_core.sendto(b'ok', addr)
                recv_content_length += len(chunk)
                recv_content += chunk
                # 打印接收进度
                # print('\r', recv_content_length, content_length, end='')
            # 打印换行符
            # print()
            # 将二进制文本转换为ASCII文本
            text = recv_content.decode('utf-8-sig')
            # 文本消息保存到本地
            with open(save_path, 'ab') as f:
                f.write(f'<p sender="{base64.b64decode(headers["sender"].encode()).decode()}" st="{headers["ct"]}" '
                        f'type="receive">'
                        f'{text}'
                        f'</p>\n'.encode())
            return headers, headers['md5'] == hashlib.md5(recv_content).hexdigest(), text

    def handle_register_rsp(self, headers, addr):
        """分析服务端处理注册请求的响应头"""
        # code == 1，注册失败，用户名已存在
        if headers['code'] == 1:
            return headers, False
        # code == 0，注册成功
        elif headers['code'] == 0:
            return headers, True

    def handle_login_rsp(self, headers, addr):
        """分析处理服务端处理登录请求的响应头"""
        # 登录成功
        if headers['code'] == 0:
            return headers, True
        # 登录失败
        else:
            return headers, False

    def handle_online_users(self, headers):
        """解析在线用户"""
        online_users: dict = headers['content']
        print(online_users.keys(), self.curr_users.keys())
        new_online_users = set(online_users.keys()).difference(self.curr_users.keys())
        self.new_online_users.clear()
        for i in new_online_users:
            self.new_online_users[i] = tuple(online_users.get(i))
        for i in online_users:
            self.curr_users[i] = tuple(online_users[i])

    def get_user_from_addr(self, addr):
        for i in self.curr_users:
            if self.curr_users[i] == addr:
                return i
        else:
            return 'server'

    def ask_for_profile(self, user, server_addr):
        headers = {
            "code": 0,
            "type": "ProfileRequest",
            "sender": base64.b64encode(self.account_id.encode()).decode(),
            "content": base64.b64encode(user.encode()).decode(),
            "ct": get_curr_time()
        }
        self.sendto(headers, server_addr)

    def upload_profile(self, profile: list|tuple, server_addr):
        headers = {
            "code": 0,
            "type": "UploadProfile",
            "sender": base64.b64encode(self.account_id.encode()).decode(),
            "content": profile,
            "ct": get_curr_time()
        }
        self.sendto(headers, server_addr)

    def upload_avatar(self, byte_file, server_addr):
        md5 = os.path.splitext(os.path.basename(byte_file))[0]
        self.send_content_to(byte_file=byte_file, addr=server_addr, add={"content": md5, "type": "UploadAvatar"})

    def handle_profile(self, headers):
        """处理用户资料"""
        profile = headers['content']
        """{
            "code": 0,
            "type": "profile",
            "sender": "server",
            "content": [username, uid, register_date, birthday, age, brief_intro]
            "ct": str(time)
            }
        """
        return profile

    def ask_for_avatar(self, account_id, server_addr):
        file_path = os.listdir(f'.local/data/{account_id}/avatar/')
        if file_path:
            md5 = os.path.splitext(file_path[0])[0]
        else:
            md5 = ''
        headers = {
            "code": 0,
            "type": "AvatarRequest",
            "sender": base64.b64encode(self.account_id.encode()).decode(),
            "target": base64.b64encode(account_id.encode()).decode(),
            "content": md5,
            "ct": get_curr_time()
        }
        self.sendto(headers, server_addr)

    def ask_for_unread_messages(self, account_id, server_addr):
        headers = {
            "code": 0,
            "type": "UnreadMsgRequest",
            "sender": base64.b64encode(self.account_id.encode()).decode(),
            "target": base64.b64encode(account_id.encode()).decode(),
            "ct": get_curr_time()
        }
        self.sendto(headers, server_addr)

    def search_user(self, account_id, server_addr):
        headers = {
            'code': 0,
            'type': 'SearchUser',
            'sender': base64.b64encode(self.account_id.encode()).decode(),
            'target': base64.b64encode(account_id.encode()).decode(),
            'ct': get_curr_time()
        }
        if os.path.exists(f'./.local/data/{account_id}/avatar') and os.listdir(f'./.local/data/{account_id}/avatar'):
            headers['avatar'] = False
        else:
            headers['avatar'] = True
        self.sendto(headers, server_addr)

    def send_fri_req(self, account_id, server_addr):
        headers = {
            'code': 0,
            'type': 'FriReq',
            'sender': base64.b64encode(self.account_id.encode()).decode(),
            'target': base64.b64encode(account_id.encode()).decode(),
            'ct': get_curr_time()
        }
        self.sendto(headers, server_addr)

    def handle_fri_req(self, *args):
        sender, accept, server_addr, idx = args if len(args) == 3 else args[0]
        headers = {
            'code': 0 if accept else 1,
            'type': 'FriReq-Response' if accept else 'FriReq-Response',
            'sender': base64.b64encode(self.account_id.encode()).decode(),
            'target': base64.b64encode(sender.encode()).decode(),
            'id': idx,
            'ct': get_curr_time()
        }
        self.sendto(headers, server_addr)

    def del_offline_msg_by_id(self, idx, server_addr):
        self.sendto(
            {
                'code': 0,
                'type': 'delete-offline-msg',
                'id': idx,
                'sender': base64.b64encode(self.account_id.encode()).decode()
            },
            server_addr)

    def log_out(self, server_addr):
        self.sendto(
            {
                "code": 0,
                "type": "logout",
                "sender": base64.b64encode(self.account_id.encode()).decode(),
                "ct": get_curr_time()
            },
            server_addr
        )


if __name__ == '__main__':
    test = ClientCore(('localhost', 8091), ('localhost', 8092))
    # a = test.core.getsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF)
    # print(a)

    test.signOut(("localhost", 8080))

    # test.login('Ass123', 'Ass123', ("localhost", 8080))
    # headers, addr = test.recv_from()
    # rsp = test.handle_login_rsp(headers, addr)
    # print(rsp)
    # headers, addr = test.recv_from()
    # print(str(headers))
    # test.handle_online_users(headers)


    # text = open('ships.json', 'r', encoding='utf-8-sig').read()
    # test.send_content_to(byte_file=r'C:\Users\ArcueidBrunestud\Desktop\ShikiChat\TCP\shiki.rar', addr=('localhost', 8080))