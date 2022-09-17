# Shiki处理用户操作的工具
import configparser


class UserList:

    def __init__(self, type: str):
        self.__Config = configparser.ConfigParser()
        self.path = f'.\\Server\\cache\\{type}\\UserConfig.ini'
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

    def get(self, Username, Option):
        return self.__Config.get(Username, Option)


if __name__ == '__main__':
    userList = UserList('client')
    userList.add('Artoria', {"PASSWORD": "I-LOVE-ARTORIA", "AUTOFILL":"True"})
    userList.add('Shiki', {"PASSWORD": "I-LOVE-SHIKI","AUTOFILL":"True"})
    userList.save()
    userList.update()
    print('Shiki' in userList)




