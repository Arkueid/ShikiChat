import base64
import hashlib
import io
import json
import os
import bs4
import sys
from modules.client_core import ClientCore
from GUI.main_chat_win import MainChatWin
from GUI.entrance import Entrance
from GUI.info_page import InfoPage
from PyQt5.QtWidgets import QApplication, QMessageBox, QFileDialog, QListWidget, QListWidgetItem
from PyQt5.QtGui import QIcon, QPixmap
from modules.utils import Signals
from GUI.chatroom import ChatRoom
import threading
from PIL import Image
from modules.utils import get_curr_time
from PyQt5.QtCore import QSize


class Main:
    """主程序"""
    # 信号合集，用于线程之间的通信
    signals = Signals()

    def __init__(self, send_core_addr, recv_core_addr):
        # Qt 运行环境
        self.app = QApplication(sys.argv)
        # 登录/注册窗口
        self.entrance_win = Entrance()
        # 资料窗口
        self.info_page = InfoPage(('0', '0', '1000-01-01 00:00:00', '1000-1-1 00:00:00', '1', 'no intro'),
                                  'default.png')
        # 客户端核心、收发逻辑
        self.client = ClientCore(send_core_addr, recv_core_addr)
        # 服务端ip和端口
        self.server_addr = ('localhost', 8080)
        # 设置信号、初始化信号
        self.setupSignals()

    def run(self):
        """启动窗口、主程序的入口"""
        self.entrance_win.show()
        sys.exit(self.app.exec_())

    def handle_messages(self):
        """处理消息、放在子线程中运行"""
        while True:
            # 接收数据报
            headers, addr = self.client.recv_from()
            print(headers)
            # 根据数据报类型选择相应处理方式

            # 数据传输部分
            # 接收其他用户发来的消息
            if headers['type'] == 'message':
                self.receive_message_from(headers, addr)
            # 接收在线用户列表
            elif headers['type'] == 'online users':
                self.client.handle_online_users(headers)
                self.signals.receive_online_users.emit()
            # 接收个人资料的信息列表
            elif headers['type'] == 'profile':
                self.signals.receive_profile.emit(headers)
            # 接收头像文件
            elif headers['type'] == 'avatar':
                self.handle_avatar(headers, addr)

            # 服务器响应部分，仅包含数据报处理
            # 接收服务器响应，上传个人资料提交成功
            elif headers['type'] == 'ProfileUploadSuccess':
                # print('资料修改成功!')
                pass
            # 接收服务端响应，头像上传成功或上传的头像和服务端储存头像是同一张，即md5值相同
            elif headers['type'] == ('AvatarUploadSuccess' or 'AvatarIsSame'):
                # print('头像修改成功!')
                pass
            # 接收服务器响应，头像已经是最新的
            elif headers['type'] == 'AvatarIsLatest':
                # print(base64.b64decode(headers['target']).decode(), '头像已是最新!')
                pass

            elif headers['type'] == 'UserSearchResponse':
                self.handle_user_search_response(headers, addr)

            elif headers['type'] == 'FriReq':
                self.handle_fri_req(headers)

            elif headers['type'] == 'FriReq-Response':
                self.handle_fri_req_response(headers)

            elif headers['type'] == 'FriAlready':
                self.signals.fri_already_warning.emit(headers['target'])

            elif headers['type'] == 'offline-msg':
                self.handle_offline_msg(headers)

    def setupSignals(self):
        # 登录页面的登录按钮点击后执行Main.login()函数
        self.entrance_win.Login.button_login.clicked.connect(self.login)
        # 注册页面的注册按钮点击后执行Main.register()函数
        self.entrance_win.Register.button_register.clicked.connect(self.register)
        # Main.signals发出receive_message信号（收到其他用户发来的消息）之后执行Main.handle_message()方法
        self.signals.receive_message.connect(self.handle_message)
        # 接收到在线用户列表之后执行self.handle_online_users()方法
        self.signals.receive_online_users.connect(self.handle_online_users)
        # 接收到个人资料后执行self.show_info_page()（弹出个人资料窗口）
        self.signals.receive_profile.connect(self.show_info_page)
        # 点击个人资料页面的确认按钮执行self.upload_profile()（向服务器提交个人资料）
        self.info_page.btn_confirm.clicked.connect(self.upload_profile)
        # 接收到头像文件后更新窗口中对应用户的头像
        self.signals.receive_avatar.connect(self.update_avatar)

        self.signals.fri_already_warning.connect(self.handle_fri_already)

        self.signals.receive_fri_req.connect(self.insert_mail)

        self.signals.receive_fri_req_accepted.connect(self.insert_fri_req_accepted)

    def login(self):
        """登录函数，登录页面的登录按钮被点击后执行"""
        # 从用户名输入框中获取已经输入的用户名
        account_id = self.entrance_win.Login.lineEdit_username.text()
        # 从密码输入框中获取已输入的密码
        password = self.entrance_win.Login.lineEdit_password.text()
        # 用户名和密码其中之一为空字符串则函数停止并返回None
        # 如果均不为空字符则继续执行if判断下方的代码
        if not account_id or not password:
            return
        # 尝试向服务器发送登录信息
        # 如果报错仅可能为服务器未启动
        # 则执行服务器未启动时的处理代码
        try:
            # 通过客户端核心发送登录信息
            self.client.login(account_id, password, self.server_addr)
            # 接收服务端的数据报
            headers, addr = self.client.recv_from()
            # 处理数据报，整理返回有用信息
            rsp = self.client.handle_login_rsp(headers, addr)
            # rsp[1] == True，表明登录成功
            if rsp[1]:
                # 弹出消息框，提示登录成功
                QMessageBox.information(self.entrance_win, "登录", "登录成功!", buttons=QMessageBox.Close)
                print(f"{addr}\n{headers}")
                # 启动主聊天窗口
                self.run_main_chat_win(account_id)
            elif rsp[0]['type'] == "LoginUserError":
                QMessageBox.information(self.entrance_win, "登录", "该用户已登录!", buttons=QMessageBox.Close)
                print(f"{addr}\n{headers}")
                self.entrance_win.Login.lineEdit_password.clear()
            elif rsp[0]['type'] == "LoginAccountError":
                QMessageBox.information(self.entrance_win, "登录", "用户名不存在!", buttons=QMessageBox.Close)
                print(f"{addr}\n{headers}")
                self.entrance_win.Login.lineEdit_password.clear()
            elif rsp[0]['type'] == "LoginPasswordError":
                QMessageBox.information(self.entrance_win, "登录", "密码错误!", buttons=QMessageBox.Close)
                print(f"{addr}\n{headers}")
                self.entrance_win.Login.lineEdit_password.clear()
        except ConnectionResetError:
            QMessageBox.information(self.entrance_win, "登录", "服务器未启动!", buttons=QMessageBox.Close)

    def register(self):
        # 获取注册页面的用户名，密码，确认密码
        account_id = self.entrance_win.Register.lineEdit_username.text()
        password = self.entrance_win.Register.lineEdit_password.text()
        confirm_password = self.entrance_win.Register.lineEdit_check_password.text()
        # 分析用户名、密码、确认密码是否符号规范，若是则向服务器发起注册请求
        # 两次输入密码是否相等
        if password == confirm_password:
            # 向服务器发起请求，如果发送失败则弹出服务器未启动的消息弹窗
            try:
                # 通过客户端发起注册，客户端的register函数包含检测输入是否规范
                # 返回处理结果
                rsp = self.client.register(account_id, password, self.server_addr)
                # 密码符合规范，并已经向服务器发起请求
                if rsp == 0:
                    headers, addr = self.client.recv_from()
                    rsp = self.client.handle_register_rsp(headers, addr)
                    # rsp[1] 为真，说明注册成功
                    if rsp[1]:
                        QMessageBox.information(self.entrance_win, "注册", "注册成功!", buttons=QMessageBox.Close)
                        # 清空输入的用户名，密码，确认密码
                        self.entrance_win.Register.lineEdit_username.clear()
                        self.entrance_win.Register.lineEdit_password.clear()
                        self.entrance_win.Register.lineEdit_check_password.clear()
                    # 用户已被注册
                    else:
                        QMessageBox.information(self.entrance_win, "注册", "用户名已被注册!", buttons=QMessageBox.Close)
                        self.entrance_win.Register.lineEdit_username.clear()
                        self.entrance_win.Register.lineEdit_password.clear()
                        self.entrance_win.Register.lineEdit_check_password.clear()
                # 密码不符合规范，未向客户端发送请求
                elif rsp == 1:
                    QMessageBox.information(self.entrance_win, "注册", "密码必须包含数字、大小写字母和下划线!", buttons=QMessageBox.Close)
                    self.entrance_win.Register.lineEdit_password.clear()
                    self.entrance_win.Register.lineEdit_check_password.clear()
                elif rsp == 2:
                    QMessageBox.information(self.entrance_win, "注册", "密码长度应为6-16位!", buttons=QMessageBox.Close)
                    self.entrance_win.Register.lineEdit_password.clear()
                    self.entrance_win.Register.lineEdit_check_password.clear()
                elif rsp == 3:
                    QMessageBox.information(self.entrance_win, "注册", "账号应包含数字，大小写字母!", buttons=QMessageBox.Close)
                    self.entrance_win.Register.lineEdit_password.clear()
                    self.entrance_win.Register.lineEdit_check_password.clear()
                elif rsp == 4:
                    QMessageBox.information(self.entrance_win, "注册", "账号长度应为6-16位!", buttons=QMessageBox.Close)
                    self.entrance_win.Register.lineEdit_password.clear()
                    self.entrance_win.Register.lineEdit_check_password.clear()
            except ConnectionResetError:
                QMessageBox.information(self.entrance_win, "注册", "服务器未启动!", buttons=QMessageBox.Close)
        else:
            QMessageBox.information(self.entrance_win, "注册", "两次密码不一致!", buttons=QMessageBox.Close)
            self.entrance_win.Register.lineEdit_password.clear()
            self.entrance_win.Register.lineEdit_check_password.clear()

    def run_main_chat_win(self, user):
        """启动聊天窗口，即登录成功后启动主界面"""
        # 关闭登录注册窗口
        self.entrance_win.close()
        # 回收对象
        del self.entrance_win
        # 接收并处理在线用户列表
        headers, addr = self.client.recv_from()
        # 把在线用户添加到客户端的在线用户列表
        self.client.handle_online_users(headers)
        # 创建主聊天窗口
        self.main_chat_win = MainChatWin(user)
        # 根据在线用户列表中的用户添加子聊天窗口，并把在线用户添加到主窗口的在线用户列表
        for user in self.client.curr_users:
            addr = self.client.curr_users[user]
            chatroom = self.main_chat_win.add_user(user, self.get_file_from(user, 'avatar'), addr)
            chatroom.btn_send.clicked.connect(self.send_message_to)
        # 读取本地头像
        self.main_chat_win.user_list_win.profile.avatar.setPixmap(QPixmap(self.get_file_from(user, 'avatar')))
        # 设置聊天主窗口信号
        self.main_chat_win.user_list_win.profile.btn_eidt.clicked.connect(self.ask_for_profile)
        # 双击头像修改头像
        self.main_chat_win.user_list_win.profile.avatar.doubleClicked.connect(self.edit_avatar)
        # 点击在线用户获取头像
        self.main_chat_win.user_list_win.user_list.clicked.connect(self.ask_for_avatar)
        # 添加好友搜索窗口
        self.fri_add_page = self.main_chat_win.fri_add_page
        # 点击添加好友弹出添加页面
        self.main_chat_win.user_list_win.action_add_fri.triggered.connect(self.fri_add_page.window.show)
        self.main_chat_win.user_list_win.action_logout.triggered.connect(self.logout)
        self.fri_add_page.btn_search.clicked.connect(self.search_user)
        # 点击添加好友发送好友请求
        self.fri_add_page.btn_add_fri_req.clicked.connect(self.send_fri_req)
        # 拉取在线用户本地历史消息
        for account_id in self.client.curr_users:
            self.get_last_messages(account_id)
        # 开启接收核心的线程
        t = threading.Thread(target=self.handle_messages, daemon=True)
        t.start()
        self.main_chat_win.splitter.show()

    def handle_online_users(self):
        """处理在线用户"""
        for user in self.client.new_online_users:
            addr = self.client.new_online_users[user]
            # 添加对应用户的子聊天窗口
            chatroom = self.main_chat_win.add_user(user, '', addr)
            # 对发送按钮设置信号
            chatroom.btn_send.clicked.connect(self.send_message_to)

    def receive_message_from(self, headers, addr, offline=False):
        """接收消息"""
        # 根据数据包内数据类型和数据长度选取对应方式接收数据
        save_root = self.init_cache_dir(self.client.account_id,
                                        f'messages/{base64.b64decode(headers["sender"].encode()).decode()}/')
        if not offline:
            rsp = self.client.handle_content(headers, addr,
                                             save_path=os.path.join(save_root, get_curr_time("day") + '.html'))
            # 处理的是文件类型则rsp[0]为字符串
            if type(rsp[0]) == str:
                print(rsp)
                return
        else:
            save_path = os.path.join(save_root, get_curr_time("day") + '.html')
            rsp = headers, True, headers['content']
            with open(save_path, 'ab') as f:
                f.write(f'<p sender="{base64.b64decode(headers["sender"].encode()).decode()}" st="{headers["ct"]}" '
                        f'type="receive">'
                        f'{rsp[-1]}'
                        f'</p>\n'.encode())
        # 不是则发出接收到来自其他用户消息的信号
        self.signals.receive_message.emit(rsp)

    def handle_message(self, rsp):
        """处理接收到的消息"""
        # 把消息转换为气泡元件并添加到聊天窗口
        headers = rsp[0]
        # 发送者UID/用户名
        account_id = base64.b64decode(headers['sender'].encode()).decode()
        # 找到发送者对应的接收窗口
        chatroom: ChatRoom = self.main_chat_win.chatroom_ls[account_id]
        # 把消息气泡添加到聊天窗口
        chatroom.add_item(account_id, self.client.account_id, content=rsp[2])

    def send_message_to(self, text=None, text_file=None, byte_file=None):
        """直接发送消息给其他客户端"""
        chatroom: ChatRoom = self.main_chat_win.current_chatroom
        text = chatroom.textEdit.toPlainText()
        if not text:
            return
        user, addr = self.main_chat_win.user_list_win.user_list.currentItem().data(5)
        try:
            self.client.send_content_to(text, text_file, byte_file, addr=addr, add={"receiver": user})
            # 文本消息本地保存...
            save_root = self.init_cache_dir(self.client.account_id,
                                            f'messages/{user}/')
            save_path = os.path.join(save_root, get_curr_time("day") + '.html')
            with open(save_path, 'ab') as f:
                f.write(f'<p sender="{self.client.account_id}" st="{get_curr_time()}" '
                        f'type="send">'
                        f'{text}'
                        f'</p>\n'.encode())
            # 聊天窗口添加相应聊天气泡
            chatroom.add_item(self.client.account_id, user, type_='send',
                              content_type='text', content=text,
                              avatar=self.main_chat_win.user_list_win.profile.avatar.pixmap())
        except Exception as e:
            print(e)
            QMessageBox.information(self.main_chat_win.splitter, '发送消息', '消息发送失败!', buttons=QMessageBox.Close)
        chatroom.textEdit.clear()

    def show_info_page(self, headers, avatar='default.png'):
        root = f'.local/data/{headers["content"][0]}/avatar/'
        ls = os.listdir(root)
        if ls:
            avatar = root + ls[0]
        self.info_page.load_profile_from(headers['content'], avatar)
        self.info_page.setSelf(True)
        self.info_page.show()

    def upload_profile(self):
        if len(self.info_page.ldt_brief_introduction.toPlainText()) > 50:
            QMessageBox.information(self.info_page, '保存资料', '简介不能超过50个字!', buttons=QMessageBox.Close)
            return
        pf = (
            self.info_page.ldt_username.text(),
            self.info_page.ldt_birthday.text(),
            self.info_page.ldt_age.text(),
            self.info_page.ldt_brief_introduction.toPlainText()
        )
        if all(pf):
            self.client.upload_profile(pf, self.server_addr)
        else:
            QMessageBox.information(self.info_page, '保存资料', '信息不能为空!', buttons=QMessageBox.Close)

    def ask_for_profile(self):
        self.client.ask_for_profile(self.client.account_id, self.server_addr)

    def ask_for_avatar(self):
        account_id = self.main_chat_win.user_list_win.user_list.currentItem().data(5)[0]
        self.client.ask_for_avatar(account_id, self.server_addr)

    def handle_avatar(self, headers, addr):
        account_id = base64.b64decode(headers['target']).decode()
        for i in os.listdir(f'.local/data/{account_id}/avatar/'):
            os.remove(f'.local/data/{account_id}/avatar/' + i)
        rsp = self.client.handle_content(headers, addr, save_path=f'.local/data/{account_id}/avatar/')
        self.signals.receive_avatar.emit(account_id)
        print(rsp)

    def update_avatar(self, account_id):
        root = f'.local/data/{account_id}/avatar/'
        avatar_path = root + os.listdir(root)[0]
        for i in range(self.main_chat_win.user_list_win.user_list.count()):
            item = self.main_chat_win.user_list_win.user_list.item(i)
            print(item.data(5))
            if item.data(5)[0] == account_id:
                item.setIcon(QIcon(avatar_path))
                print(1)
                return

    def edit_avatar(self):
        desktop_path = os.path.join(os.path.expanduser('~'), 'Desktop')
        path, type_ = QFileDialog.getOpenFileName(self.main_chat_win.splitter, '头像编辑', desktop_path,
                                                  filter='*.png;*.jpeg;*.jpg;*tif;*.webp')
        if path:
            f = open(path, 'rb')
            content = f.read()
            f.close()
            md5 = hashlib.md5(content).hexdigest()
            ls = os.listdir(f'.local/data/{self.client.account_id}/avatar/')
            save_path = f'.local/data/{self.client.account_id}/avatar/{md5}.png'
            if ls:
                os.remove(f'.local/data/{self.client.account_id}/avatar/' + ls[0])
            img = Image.open(io.BytesIO(content))
            del content
            img = img.resize((100, 100))
            img.save(save_path)
            self.client.upload_avatar(save_path, self.server_addr)
            self.main_chat_win.user_list_win.profile.avatar.setPixmap(QPixmap(save_path))
            self.update_avatar(self.client.account_id)
        else:
            print('未选中图片!')

    def init_cache_dir(self, account_id, section):
        path = f".local/data/{account_id}/{section}/"
        if not os.path.exists(path):
            os.makedirs(path)
        return path

    def get_file_from(self, account_id, section, opt=0):
        root = f".local/data/{account_id}/{section}/"
        self.init_cache_dir(account_id, section)
        file = os.listdir(root)
        file = file[0] if file else os.listdir(f'.local/default/{section}/')[0]
        return root + file

    def get_last_messages(self, user):
        chatroom = self.main_chat_win.chatroom_ls[user]
        path = f'.local/data/{self.client.account_id}/messages/{user}/{get_curr_time("day")}.html'
        if os.path.exists(path):
            soup = bs4.BeautifulSoup(open(path, 'rb').read().decode(), 'lxml').find_all('p')
            for i in soup:
                text = i.text
                type_ = i.attrs['type']
                if type_ == 'receive':
                    sender = i.attrs['sender']
                    chatroom.add_item(sender, '', content=text)
                else:
                    sender = self.client.account_id
                    chatroom.add_item(sender, '', type_='send', content=text,
                                      avatar=self.main_chat_win.user_list_win.profile.avatar.pixmap())
            if soup:
                msg_ls: QListWidget = chatroom.messageList
                msg_ls.addItem(QListWidgetItem('以上为历史消息'))

    def search_user(self):
        account_id = self.fri_add_page.led_search.text()
        print(account_id)
        self.fri_add_page.result_ls.clear()
        if account_id:
            self.client.search_user(account_id, self.server_addr)

    def handle_user_search_response(self, headers, addr):
        for uid in headers['content']:
            self.fri_add_page.add_result(uid, QIcon(
                QPixmap(f'.local/data/{uid}/avatar/' + os.listdir(f'.local/data/{uid}/avatar')[0])))

    def send_fri_req(self):
        account_id = self.fri_add_page.result_ls.currentItem().text()
        if account_id:
            self.client.send_fri_req(account_id, self.server_addr)

    def handle_fri_req(self, headers):
        account_id = base64.b64decode(headers['sender'].encode()).decode()
        pixmap = QPixmap(f'.local/data/{account_id}/avatar/' + os.listdir(f'.local/data/{account_id}/avatar/')[0])
        self.signals.receive_fri_req.emit((account_id, pixmap, headers['id']))

    def insert_mail(self, data):
        UI_form = self.main_chat_win.mailbox_page.add_mail(data[0], data[1], self.server_addr, data[2])
        UI_form.accept_btn.clicked.connect(self.client.handle_fri_req)
        UI_form.accept_btn.clicked.connect(self.del_offline_msg_from_server)

    def handle_fri_req_response(self, headers):
        accept = headers['code']
        print(headers)
        self.signals.receive_fri_req_accepted.emit((base64.b64decode(headers['sender'].encode()).decode(), accept))

    def insert_fri_req_accepted(self, data):
        account_id = data[0]
        if data[1] == 0:
            pixmap = QPixmap(f'.local/data/{account_id}/avatar/' + os.listdir(f'.local/data/{account_id}/avatar/')[0])
            item = QListWidgetItem(account_id + '同意了好友请求')
            item.setIcon(QIcon(pixmap))
            item.setSizeHint(QSize(70, 70))
            self.main_chat_win.mailbox_page.mail_ls.addItem(item)
        else:
            pixmap = QPixmap(f'.local/data/{account_id}/avatar/' + os.listdir(f'.local/data/{account_id}/avatar/')[0])
            item = QListWidgetItem(account_id + '拒绝了好友请求')
            item.setIcon(QIcon(pixmap))
            item.setSizeHint(QSize(70, 70))
            self.main_chat_win.mailbox_page.mail_ls.addItem(item)

    def handle_fri_already(self, user):
        QMessageBox.information(self.fri_add_page.window, '添加好友', f'{user}已经是好友！', buttons=QMessageBox.Yes)

    def handle_offline_msg(self, headers):
        for sub_headers in headers['content']:
            sub_headers = json.loads(sub_headers)
            if sub_headers['type'] == 'FriReq':
                self.handle_fri_req(sub_headers)

            elif sub_headers['type'] == 'FriReq-Response':
                self.handle_fri_req_response(sub_headers)
                self.client.sendto(
                    {
                        'code': 0,
                        'type': 'delete-offline-msg',
                        'id': sub_headers['id'],
                        'sender': base64.b64encode(self.client.account_id.encode()).decode()
                    },
                    self.server_addr)

            elif sub_headers['type'] == 'message':
                self.receive_message_from(sub_headers, '', offline=True)

    def del_offline_msg_from_server(self, data):
        self.client.del_offline_msg_by_id(data[-1], self.server_addr)

    def logout(self):
        self.client.log_out(self.server_addr)
        self.main_chat_win.splitter.hide()
        sys.exit()


if __name__ == '__main__':
    test = Main(('localhost', 8091), ('localhost', 8092))
    test.run()
