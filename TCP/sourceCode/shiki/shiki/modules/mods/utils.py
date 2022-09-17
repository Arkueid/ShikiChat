"""
用户本地配置信息配置工具
"""
# Shiki处理用户操作的工具
import configparser
import os.path


class UserList:

    def __init__(self, type_: str):
        self.__Config = configparser.ConfigParser()
        self.rootPath = f"./{type_.capitalize()}/cache/{type_}/"
        if not os.path.exists(self.rootPath):
            os.mkdir(self.rootPath)
        self.path = self.rootPath + 'UserConfig.ini'
        if not os.path.exists(self.path):
            f = open(self.path,'w')
            f.close()
        self.update()

    def __iter__(self):
        return iter(self.__Config)

    def __str__(self):
        return str(self.__Config.sections())

    def __len__(self):
        return len(self.__Config.sections())

    def __getitem__(self, item):
        return self.__Config[item]

    def save(self):
        with open(self.path,'w+') as f:
            self.__Config.write(f)

    def remove(self, Username: str):
        self.__Config.remove_section(Username)

    def users(self):
        return self.__Config.sections()

    def update(self):
        for i in self.__Config.sections():
            self.__Config.remove_section(i)
        self.__Config.read(self.path)

    def add(self, Username: str, info: dict):
        self.__Config[Username] = info

    def get(self, Username, Option, default=None):
        try:
            if Username != 'DEFAULT':
                return self.__Config.get(Username, Option)
        except:
            return default


if __name__ == '__main__':
    userList = UserList('client')
    userList.add('Artoria', {"PASSWORD": "I-LOVE-ARTORIA", "AUTOFILL":"True"})
    userList.add('Shiki', {"PASSWORD": "I-LOVE-SHIKI","AUTOFILL":"True"})
    userList.save()
    userList.update()
    print('Shiki' in userList)




