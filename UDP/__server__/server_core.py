import base64
import hashlib
import socket
import pymysql as sql
import struct
import json
import threading
from utils import get_curr_time
import os


class ServerCore:

    def __init__(self, core_ip='localhost', core_port=8080):
        self.core = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # 设置ip和端口可重用，避免bind失败
        self.core.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # 限制最大线程数
        self.thread_lock = threading.Semaphore(5)
        self.core_ip = core_ip
        self.core_port = core_port
        # 服务端启动时为running=True，设置为False则服务端关闭
        self.running = False
        self.core_addr = self.core_ip, self.core_port
        self.online_users = dict()
        self.core.bind(self.core_addr)

    def run(self):
        """启动入口"""
        self.running = True
        # 最大线程数
        self.thread_lock = threading.Semaphore(5)
        while self.running:
            self.handle_connection()

    def handle_connection(self):
        headers, addr = self.recv_from()
        print("ServerCore.handle_connection:\n", addr, headers)
        if headers['code'] == 0:
            if headers['type'] == 'register':
                self.handle_register(headers, addr)
            elif headers['type'] == 'login':
                self.handle_login(headers, addr)
            elif headers['type'] == 'SignOut':
                self.handle_offline(addr)
            elif headers['type'] == 'message':
                self.handle_content(headers, addr=addr, save_path='')
            elif headers['type'] == 'UploadProfile':
                self.handle_profile_upload(headers,
                                           self.online_users[base64.b64decode(headers['sender'].encode()).decode()])
            elif headers['type'] == 'ProfileRequest':
                self.handle_profile_request(headers,
                                            self.online_users[base64.b64decode(headers['sender'].encode()).decode()])
            elif headers['type'] == 'AvatarRequest':
                self.handle_avatar_request(headers,
                                           self.online_users[base64.b64decode(headers['sender'].encode()).decode()])
            elif headers['type'] == 'UploadAvatar':
                self.handle_avatar_upload(headers,
                                           self.online_users[base64.b64decode(headers['sender'].encode()).decode()],
                                          addr)
            elif headers['type'] == 'SearchUser':
                self.handle_user_search(headers,
                                        self.online_users[base64.b64decode(headers['sender'].encode()).decode()]
                                        )
            elif headers['type'] == "FriReq":
                self.handle_fri_req(headers)
            elif headers['type'] == 'FriReq-Response':
                self.handle_fri_req_response(headers)
            elif headers['type'] == 'delete-offline-msg':
                self.handle_del_offline_msg(headers)
            elif headers['type'] == 'logout':
                self.handle_logout(headers)

    def handle_register(self, headers, addr):
        addr = tuple(headers['addr'])
        account_id = base64.b64decode(headers['account']).decode()
        password = base64.b64decode(headers['password']).decode()
        sql_conn = sql.connect(
            host='localhost',
            user='root',
            password='abdb'
        )
        try:
            sql_conn.cursor().execute('use user_list')
            sql_conn.cursor().execute('insert into login_verification values('
                                      f"0,"
                                      f'"{account_id}",'
                                      f'"{password}");')
            headers = {
                "code": 0,
                "type": "RegisterSuccess",
                "sender": "Server",
                "content": "Account registered successfully!",
                "ct": get_curr_time()
            }
            # 创建好友列表z
            sql_conn.cursor().execute('use friend_list')
            sql_conn.cursor().execute(f'create table user{hashlib.md5(account_id.encode()).hexdigest()}('
                                      'id int primary key auto_increment,'
                                      'fri_account_id varchar(16) not null unique,'
                                      'is_fri bool not null);')
            sql_conn.cursor().execute('use offline_message')
            # 创建离线信息表
            sql_conn.cursor().execute(f'create table user{hashlib.md5(account_id.encode()).hexdigest()}('
                                      'id int primary key auto_increment,'
                                      f'account_id varchar(16) not null,'
                                      'headers json not null);')
            sql_conn.cursor().execute('use user_list;')
            sql_conn.cursor().execute('insert into basic_info values('
                                      '0,'
                                      f'"{account_id}",'
                                      f'"{"用户" + account_id}",'
                                      f'"{get_curr_time()}",'
                                      f'"{get_curr_time("day")}",'
                                      f'default,'
                                      f'default,'
                                      f'default,'
                                      f'default);')
            sql_conn.commit()
            # 返回处理结果给客户端
            self.sendto(headers, addr)
        except sql.err.IntegrityError:
            headers = {
                "code": 1,
                "type": "RegisterAccountError",
                "sender": "server",
                "content": "Account already exists!",
                "ct": get_curr_time()
            }
            self.sendto(headers, addr)
        finally:
            sql_conn.close()

    def handle_login(self, headers, addr):
        addr = tuple(headers['addr'])
        account_id = base64.b64decode(headers['account'].encode()).decode()
        if account_id in self.online_users:
            headers = {
                "code": 1,
                "type": "LoginUserError",
                "sender": "server",
                "content": "User has already logged in!",
                "ct": get_curr_time()
            }
            self.sendto(headers, addr)
            return
        password = headers['password']
        sql_conn = sql.connect(
            host='localhost',
            user='root',
            password='abdb'
        )
        sql_conn.cursor().execute('use user_list')
        cursor = sql_conn.cursor()
        cursor.execute(f'select account_id from login_verification')
        account_ls = cursor.fetchall()
        for account in account_ls:
            if account_id == account[0]:
                cursor.execute(f'select password from login_verification where account_id="{account[0]}"')
                saved_password = cursor.fetchall()[0][0]
                # 检测密码是否正确
                if hashlib.md5(saved_password.encode()).hexdigest() == password:
                    headers = {
                        "code": 0,
                        "type": "LoginSuccess",
                        "sender": "server",
                        "content": "Logged in successfully!",
                        "ct": get_curr_time()
                    }
                    # 回应登录成功
                    self.sendto(headers, addr)
                    self.online_users[account[0]] = addr
                    print("ServerCore.handle_login:\n", self.online_users)
                    cursor.execute('use friend_list;')
                    cursor.execute(f'select fri_account_id from user{hashlib.md5(account_id.encode()).hexdigest()}')
                    online_fri_uid_ls = list(map(lambda x: x[0], cursor.fetchall()))
                    online_fri = dict()
                    for i in online_fri_uid_ls:
                        online_fri[i] = self.online_users.get(i, self.core_addr)
                    headers = {
                        "code": 0,
                        "type": "online users",
                        "sender": "server",
                        "content": online_fri,
                        "ct": get_curr_time()
                    }
                    addr2 = self.online_users[account_id]
                    self.sendto(headers, addr2)
                    cursor.execute('use offline_message')
                    cursor.execute(f'select * from user{hashlib.md5(account_id.encode()).hexdigest()}')
                    rsp = cursor.fetchall()
                    headers = {
                        'code': 0,
                        'type': 'offline-msg',
                        'sender': 'server',
                        'content': list(map(lambda x: x[2], rsp)),
                        'ct': get_curr_time()
                    }
                    self.sendto(headers, addr2)
                    sql_conn.commit()
                    # for addr in self.online_users.values():
                    #     self.sendto(headers, addr)
                else:
                    headers = {
                        "code": 1,
                        "type": "LoginPasswordError",
                        "sender": "server",
                        "content": "Wrong password!",
                        "ct": get_curr_time()
                    }
                    # 回应登录失败
                    self.sendto(headers, addr)
                break
        else:
            headers = {
                "code": 1,
                "type": "LoginAccountError",
                "sender": "server",
                "content": "No such user!",
                "ct": get_curr_time()
            }
            # 回应用户不存在
            self.sendto(headers, addr)
        cursor.close()
        sql_conn.close()

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
        self.core.sendto(headers_len, addr)
        self.core.sendto(headers, addr)

    def recv_from(self):
        """
        常用接收代码串，避免重复
        :return: 接收到的数据报headers（字典）和发送者的地址addr（元组）
        """
        # 接收数据报长度
        headers_len, addr = self.core.recvfrom(4)
        headers_len = struct.unpack('i', headers_len)[0]
        # 接收数据报
        headers, addr = self.core.recvfrom(headers_len)
        headers = json.loads(headers.decode())
        return headers, addr

    def handle_offline(self, addr):
        for i in self.online_users:
            if addr == self.online_users[i]:
                del self.online_users[i]
                break
        for addr in self.online_users.values():
            headers = {
                "code": 0,
                "type": "online users",
                "sender": "server",
                "content": self.online_users,
                "ct": get_curr_time()
            }
            self.sendto(headers, addr)

    def handle_content(self, headers, addr, save_path=''):
        """处理接收数据报以外的数据"""
        # 接收数据
        type_ = headers['type']
        # 判断数据是否为文件
        if 'file' in headers['content-type']:
            # 合成文件路径
            file_name = os.path.join(save_path, f"{headers['md5']}{headers['content-type'].split('/')[-1]}")
            # 检测文件是否存在
            if not os.path.exists(save_path):
                os.makedirs(save_path)
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
                    chunk = self.core.recv(40960)
                    self.core.sendto(b'ok', addr)
                    recv_content_length += len(chunk)
                    with open(file_name, 'a', encoding='utf-8') as f:
                        f.write(chunk.decode())
                    # print('\r', recv_content_length, content_length, end='')
                # print()
                # 判断文件完整性
                # 判断接收的数据md5值是否和数据报中md5值相符
                if headers['md5'] == hashlib.md5(open(file_name, 'r', encoding='utf-8').read().encode()).hexdigest():
                    headers['file_path'] = file_name
                    if type_ == 'message':
                        conn = sql.connect(host='localhost', user='root', password='abdb')
                        conn.cursor().execute('use offline_message;')
                        conn.cursor().execute(f'insert into {headers["receiver"]} values('
                                              f'0,'
                                              f'"{self.get_user_from_addr(addr)}",'
                                              f'{json.dumps(json.dumps(headers))});')
                        conn.commit()
                        conn.close()
                    return f"\n{headers['content-type']}, {os.path.getsize(file_name)}/{headers['content-length']}", True
                else:
                    headers = {
                        "code": 1,
                        "type": "MessageError",
                        "sender": "server",
                        "content": "The file is broken!",
                        "ct": get_curr_time()
                    }
                    self.sendto(headers, addr)
                    return f"\n{headers['content-type']}, {os.path.getsize(file_name)}/{headers['content-length']}", False
            else:
                content_length = headers['content-length']
                recv_content_length = 0
                while recv_content_length < content_length:
                    # 读取一个数据包
                    chunk = self.core.recv(40960)
                    # 发送已接收，发送者接收才能继续发送，避免丢包
                    self.core.sendto(b'ok', addr)
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
                    headers['file_path'] = file_name
                    if type_ == 'message':
                        conn = sql.connect(host='localhost', user='root', password='abdb')
                        conn.cursor().execute('use offline_message;')
                        conn.cursor().execute(f'insert into user{hashlib.md5(headers["receiver"].encode())} values('
                                              f'0,'
                                              f'"{self.get_user_from_addr(addr)}",'
                                              f'{json.dumps(json.dumps(headers))});')
                        conn.commit()
                        conn.close()
                    return f"\n{headers['content-type']}, {os.path.getsize(file_name)}/{headers['content-length']}", True
                else:
                    headers = {
                        "code": 1,
                        "type": "MessageError",
                        "sender": "server",
                        "content": "The file is broken!",
                        "ct": get_curr_time()
                    }
                    self.sendto(headers, addr)
                    return f"\n{headers['content-type']}, {os.path.getsize(file_name)}/{headers['content-length']}", False
        else:
            content_length = headers['content-length']
            recv_content_length = 0
            recv_content = b''
            while recv_content_length < content_length:
                chunk = self.core.recv(40960)
                self.core.sendto(b'ok', addr)
                recv_content_length += len(chunk)
                recv_content += chunk
                # 打印接收进度
                # print('\r', recv_content_length, content_length, end='')
            # 打印换行符
            # print()
            # 将二进制文本转换为ASCII文本
            if headers['md5'] == hashlib.md5(recv_content).hexdigest():
                text = recv_content.decode()
                headers['content'] = text
                if type_ == 'message':
                    conn = sql.connect(host='localhost', user='root', password='abdb')
                    conn.cursor().execute('use offline_message;')
                    conn.cursor().execute(f'insert into user{hashlib.md5(headers["receiver"].encode()).hexdigest()} values('
                                          f'0,'
                                          f'"{self.get_user_from_addr(addr)}",'
                                          f'{json.dumps(json.dumps(headers))});')
                    conn.commit()
                    conn.close()
                return text, True

    def send_content_to(self, text=None, text_file=None, byte_file=None, addr=None, add: dict = None):
        """发送数据报以外的各种数据，包括文本，文本文件，二进制文件"""
        # 发送文本
        if text and not text_file and not byte_file:
            content = text.encode()
            headers = {
                "code": 0,
                "type": "message",
                "sender": "server",
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
                "sender": "server",
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
                "sender": "server",
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
                a = self.core.sendto(content[ptr:ptr + left], addr)
                ptr += left
                send_content_length += left
            else:
                # 剩余数据大于1024时，按1024长度读取
                self.core.sendto(content[ptr:ptr + 40960], addr)
                ptr += 40960
                send_content_length += 40960
            self.core.recvfrom(2)
            # 打印发送进度
            print('\r', send_content_length, content_length, end='')
        print()

    def get_user_from_addr(self, addr):
        for i in self.online_users:
            if self.online_users[i] == addr:
                return i

    def handle_profile_upload(self, headers, addr):
        """处理用户上传资料"""
        """{
                    "code": 0,
                    "type": "UploadProfile",
                    "sender": "UID",
                    "content": [username, birthday, age, brief_intro]
                    "ct": str(time)
                    }
                """
        try:
            uid = base64.b64decode(headers["sender"].encode()).decode()
            username, birthday, age, brief_intro = headers['content']
            conn = sql.connect(host='localhost', user='root', password='abdb', database='user_list')
            conn.cursor().execute(
                f'update basic_info set username="{username}", birthday="{birthday}", age={age}, brief_intro="{brief_intro}" where uid="{uid}";')
            conn.commit()
            conn.close()
            headers = {
                "code": 0,
                "type": "ProfileUploadSuccess",
                "sender": "server",
                "ct": get_curr_time()
            }
            self.sendto(headers, addr)
            print('信息修改成功!')
        except Exception as e:
            print(e)
            headers = {
                "code": 1,
                "type": "ProfileUploadError",
                "sender": "server",
                "ct": get_curr_time()
            }
            self.sendto(headers, addr)

    def handle_profile_request(self, headers, addr):
        """处理用户资料请求
            {
            "code": 0,
            "type": "profile",
            "sender": UID,
            "content": target_UID
            "ct": str(time)
            }
        """
        conn = sql.connect(host='localhost', user='root', password='abdb', database='user_list')
        cursor = conn.cursor()
        uid = base64.b64decode(headers["content"].encode()).decode()
        print(uid)
        cursor.execute(f'select * from basic_info where uid="{uid}"')
        rsp = cursor.fetchall()
        cursor.close()
        conn.close()
        uid, username, register_date, birthday, age, brief_intro = rsp[0][1:-2]
        headers = {
            "code": 0,
            "type": "profile",
            "sender": "server",
            "content": [uid, username, str(register_date), str(birthday), age, brief_intro],
            "ct": get_curr_time()
        }
        self.sendto(headers, addr)

    def handle_avatar_request(self, headers, addr):
        md5 = headers['content']
        conn = sql.connect(host='localhost', user='root', password='abdb', db='user_list')
        cursor = conn.cursor()
        uid = base64.b64decode(headers["target"].encode()).decode()
        cursor.execute(f'select avatar_md5, avatar_path from basic_info where uid="{uid}";')
        saved_md5, avatar_path = cursor.fetchall()[0]
        cursor.close()
        conn.close()
        if md5 != saved_md5:
            self.send_content_to(byte_file=avatar_path, addr=addr, add={"target": headers['target'], "type": "avatar"})
        else:
            headers = {
                "code": 0,
                "type": "AvatarIsLatest",
                "sender": "server",
                "target": headers['target'],
                "ct": get_curr_time()
            }
            self.sendto(headers, addr)

    def handle_avatar_upload(self, headers, recv_addr, send_addr):
        md5 = headers['content']
        uid = base64.b64decode(headers['sender'].encode()).decode()
        conn = sql.connect(
            host='localhost',
            user='root',
            password='abdb',
            db='user_list'
        )
        save_path = f'.local/data/{uid}/avatar/'
        self.handle_content(headers, send_addr, save_path)
        file_name = os.path.join(save_path, f"{headers['md5']}{headers['content-type'].split('/')[-1]}")
        conn.cursor().execute(f'update basic_info set avatar_md5="{md5}", avatar_path="{file_name}" where uid="{uid}"')
        conn.commit()
        conn.close()
        ls = os.listdir(save_path)
        if ls:
            for i in ls:
                if save_path + i != file_name:
                    os.remove(save_path + i)
        headers = {
            "code": 0,
            "type": "AvatarUploadSuccess",
            "sender": "server",
            "ct": get_curr_time()
        }
        self.sendto(headers, recv_addr)

    def init_cache_dir(self, account_id, section):
        path = f".local/data/{account_id}/{section}/"
        if not os.path.exists(path):
            os.makedirs(path)

    def get_file_from(self, account_id, section, opt=0):
        root = f".local/data/{account_id}/{section}/"
        self.init_cache_dir(account_id, section)
        file = os.listdir(root)
        file = file[0] if file else os.listdir(f'.local/default/{section}/')[0]
        return root + file

    def handle_user_search(self, headers, addr):
        send_avatar = headers['avatar']
        account_id = base64.b64decode(headers['target'].encode()).decode()
        conn = sql.connect(host='localhost', user='root', password='abdb', database='user_list')
        cursor = conn.cursor()
        cursor.execute(f'SELECT * FROM basic_info where uid regexp "{account_id}" or username regexp "{account_id}"')
        rsp = cursor.fetchall()
        cursor.close()
        conn.close()
        headers = {
            "code": 0,
            "type": "UserSearchResponse",
            "sender": "server",
            "content": [],
            "ct": get_curr_time()
        }
        for i in rsp:
            headers['content'].append(i[1])
            if send_avatar:
                self.send_content_to(byte_file=i[-2], addr=addr, add={"target": base64.b64encode(i[1].encode()).decode(), "type": "avatar"})
        self.sendto(headers, addr)

    def handle_fri_req(self, headers):
        target_account_id = base64.b64decode(headers['target'].encode()).decode()
        sender = base64.b64decode(headers['sender'].encode()).decode()
        if target_account_id in self.online_users:
            conn = sql.connect(host='localhost', user='root', password='abdb', db='friend_list')
            cursor = conn.cursor()
            cursor.execute(f'select fri_account_id from user{hashlib.md5(sender.encode()).hexdigest()};')
            fri_ls = list(map(lambda x: x[0], cursor.fetchall()))
            if target_account_id in fri_ls:
                headers = {
                    'code': 1,
                    'type': 'FriAlready',
                    'sender': 'server',
                    'target': target_account_id,
                    'ct': get_curr_time()
                }
                self.sendto(headers, self.online_users[sender])
            else:
                addr = self.online_users[target_account_id]
                conn.cursor().execute('use offline_message')
                cursor.execute(f'select max(id) from user{hashlib.md5(target_account_id.encode()).hexdigest()}')
                idx = cursor.fetchall()[0][0]
                headers['id'] = idx + 1 if idx else 0
                conn.cursor().execute(f'insert into user{hashlib.md5(target_account_id.encode()).hexdigest()} values('
                                      f'0,'
                                      f'"{sender}",'
                                      f'{json.dumps(json.dumps(headers))});')
                conn.commit()
                conn.close()
                self.sendto(headers, addr)
        else:
            conn = sql.connect(host='localhost', user='root', password='abdb', db='offline_message')
            cursor = conn.cursor()
            cursor.execute(f'select max(id) from user{hashlib.md5(target_account_id.encode()).hexdigest()}')
            idx = cursor.fetchall()[0][0]
            headers['id'] = idx + 1 if idx else 0
            conn.cursor().execute(f'insert into user{hashlib.md5(target_account_id.encode()).hexdigest()} values('
                                  f'0,'
                                  f'"{sender}",'
                                  f'{json.dumps(json.dumps(headers))});')
            conn.commit()
            conn.close()

    def handle_fri_req_response(self, headers):
        accept = headers['code']
        target = base64.b64decode(headers['target'].encode()).decode()
        sender = base64.b64decode(headers['sender'].encode()).decode()
        idx = headers['id']
        if accept == 1:
            if target in self.online_users:
                self.sendto(headers, self.online_users[target])
            else:
                conn = sql.connect(host='localhost', user='root', password='abdb', db='offline_message')
                conn.cursor().execute(f'insert into user{hashlib.md5(target.encode()).hexdigest()} values('
                                      f'0,'
                                      f'"{sender}",'
                                      f'"{headers}");')
                conn.commit()
                conn.close()
        elif accept == 0:
            conn = sql.connect(host='localhost', user='root', password='abdb', db='friend_list')
            cursor = conn.cursor()
            cursor.execute(f'select fri_account_id from user{hashlib.md5(target.encode()).hexdigest()}')
            fri_ls = tuple(map(lambda x: x[0], cursor.fetchall()))
            cursor.close()
            if sender not in fri_ls:
                conn.cursor().execute(f'insert into user{hashlib.md5(target.encode()).hexdigest()} values('
                                      f'0,'
                                      f'"{sender}",'
                                      f'1);')
                if target != sender:
                    conn.cursor().execute(f'insert into user{hashlib.md5(sender.encode()).hexdigest()} values('
                                          f'0,'
                                          f'"{target}",'
                                          f'1);')
                conn.commit()
            else:
                headers = {
                    'code': 1,
                    'type': 'FriAlready',
                    'sender': 'server',
                    'target': sender,
                    'ct': get_curr_time()
                }
                self.sendto(headers, self.online_users[sender])
            if sender in self.online_users:
                self.sendto(headers, self.online_users[sender])
                cursor = conn.cursor()
                cursor.execute('use friend_list;')
                cursor.execute(f'select fri_account_id from user{hashlib.md5(target.encode()).hexdigest()}')
                online_fri = dict(map(lambda x: (x[0], self.online_users.get(x[0], self.core_addr)), cursor.fetchall()))
                headers = {
                    "code": 0,
                    "type": "online users",
                    "sender": "server",
                    "content": online_fri,
                    "ct": get_curr_time()
                }
                cursor.close()
                self.sendto(headers, self.online_users[sender])
            else:
                conn = sql.connect(host='localhost', user='root', password='abdb', db='offline_message')
                conn.cursor().execute(f'insert into user{hashlib.md5(target.encode()).hexdigest()} values('
                                      f'0,'
                                      f'"{sender}",'
                                      f'{json.dumps(json.dumps(headers))});')
                conn.commit()
            conn.close()

    def handle_del_offline_msg(self, headers):
        idx = headers['id']
        sender = base64.b64decode(headers['sender'].encode()).decode()
        conn = sql.connect(host='localhost', user='root', password='abdb', db='offline_message')
        conn.cursor().execute(f'delete from user{hashlib.md5(sender.encode()).hexdigest()} where id={idx}')
        conn.commit()
        conn.close()

    def handle_logout(self, headers):
        user = base64.b64decode(headers['sender'].encode()).decode()
        del self.online_users[user]


if __name__ == '__main__':
    server = ServerCore()
    server.run()
