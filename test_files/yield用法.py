def send():
    content = 'abcsaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaasjsaljlsalksajlkjsalkjsaljaljsajdljlsdklasndlnsalnsdalnsdalndsknlansdklnldknalnklansdefghijklmnopqrstuvwxyz'
    ptr = 0
    read_len = 0
    global running
    read_content = ''
    content_len = len(content)
    while read_len < content_len:
        left = content_len - read_len
        if left < 4:
            chunk = content[ptr: ptr+left]
        else:
            chunk = content[ptr: ptr+4]
        ptr += len(chunk)
        read_len += len(chunk)
        read_content += chunk
        yield False
    running = False
    print('发送完毕!')
    return read_content


def handle_opt():
    for i in send():
        if not i:
            yield


def main():
    while running:
        for i in handle_opt():
            pass


if __name__ == '__main__':
    a = {1, 2, 3, 3, 3}
    print(a)
    for i in a:
        print(i)

