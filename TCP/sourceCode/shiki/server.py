from shiki import Server

if __name__ == '__main__':
    server = Server()
    print(server.ip)
    server.run()
