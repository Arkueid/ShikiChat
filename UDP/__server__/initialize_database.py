import pymysql as sql


# user_list
# |
# |_____login_verification
# |
# |_____basic_info
#
# friend_list
# |
# |_____[user_name_md5]
#
# offline_message
# |
# |_____[user_name_md5]


class DatabaseInit:

    def __init__(self):
        self.conn = sql.connect(
            host='localhost',
            user='root',
            password='abdb'
        )

    def use_database(self, database):
        self.conn.cursor().execute(f'USE {database};')

    def clear_table(self, table):
        self.conn.cursor().execute(f'delete from {table};')

    def drop_table(self, table):
        self.conn.cursor().execute(f'DROP TABLE {table};')

    def create_table_login_verification(self, place=False):
        if place:
            self.conn.cursor().execute('DROP TABLE login_verification;')
        self.conn.cursor().execute('create table login_verification('
                                   'id int primary key auto_increment,'
                                   'account_id varchar(16) unique not null,'
                                   'password varchar(16) not null);')

    def create_table_basic_info(self, place=False):
        if place:
            self.conn.cursor().execute('DROP TABLE basic_info;')
        self.conn.cursor().execute(f'create table basic_info('
                                   'id int primary key auto_increment,'
                                   'uid varchar(16) unique not null,'
                                   'username varchar(20) not null,'
                                   'register_date datetime not null,'
                                   'birthday datetime not null,'
                                   'age int not null default 1,'
                                   'brief_intro varchar(50) not null default "这个人很懒，什么也没留下。",'
                                   'avatar_path varchar(100) not null default ".local/default/a2efc5ca66af8b87c86cfd6c21f780b0.png",'
                                   'avatar_md5 varchar(50) not null default "a2efc5ca66af8b87c86cfd6c21f780b0");')

    def commit(self):
        self.conn.commit()

    def table_content(self, table, uid):
        cursor = self.conn.cursor()
        cursor.execute(f'SELECT * FROM {table} where uid="{uid}";')
        return cursor.fetchall()

    # def create_friend_list_table(self, place=False):
    #     if place:
    #         self.conn.cursor().execute('DROP TABLE basic_info;')
    #     self.conn.cursor().execute('create table ')

    def __del__(self):
        self.conn.close()

    def init_all(self, inplace=False):
        if inplace:
            try:
                self.conn.cursor().execute('DROP DATABASE user_list')
            except:
                pass
            try:
                self.conn.cursor().execute('DROP DATABASE friend_list')
            except:
                pass
            try:
                self.conn.cursor().execute('DROP DATABASE offline_message')
            except:
                pass
        self.conn.cursor().execute('CREATE DATABASE user_list')
        self.conn.cursor().execute('CREATE DATABASE friend_list')
        self.conn.cursor().execute('CREATE DATABASE offline_message')
        self.conn.cursor().execute('USE user_list')
        self.create_table_login_verification()
        self.create_table_basic_info()


if __name__ == '__main__':
   d = DatabaseInit()
   d.init_all(True)
