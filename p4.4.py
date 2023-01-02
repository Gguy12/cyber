import socket, random
import time, threading, os, datetime


def http_rcv(sock):
    body = b''
    BLOCK_SIZE = 8192
    data = sock.recv(BLOCK_SIZE)
    end_of_headers = data.find(b'\r\n\r\n')
    while end_of_headers == -1:
        _d = sock.recv(BLOCK_SIZE)
        if _d == b'':
            return b'',None
        data += _d
        end_of_headers = data.find(b'\r\n\r\n')
    end_of_headers += 4
    if b'Content-Length:'  in data[:end_of_headers]:
        len_pos = data[:end_of_headers].find(b"Content-Length:")
        len_pos +=16
        len_pos2 = data[len_pos:end_of_headers].find(b'\r\n')
        len_pos2 += len_pos
        body_size = int(data[len_pos:len_pos2])
        if len(data) > end_of_headers:
            body = data[end_of_headers:]
        while len(body) <  body_size:
            _d = sock.recv(min(BLOCK_SIZE,body_size - len(body)))
            if _d ==b'':
                return b'',None
            body += _d
    print ("RECV<<<",data[:end_of_headers],"\n100 bytes of Body: ",body[:100])
    return data[:end_of_headers] , body


def read_file(fn, ext):
    if ext == 'txt' or ext == 'css' or ext == 'js':
        read_mode = 'rb'
    else:
        read_mode= 'rb'
    with open (fn, read_mode) as f:
        data = f.read()
    if read_mode == 'r':
        return data.encode()
    return data


def build_response(request, body):
    request = request.decode()
    if request.startswith('GET'):
        all_headers = request.split('\r\n')
        fields = all_headers[0].split(' ')
        file_name = fields[1]
        if file_name == '/':
            file_name = '/index.html'
        if file_name[0] == '/':
            file_name = file_name[1:]
        if file_name.split('?')[0] == "calculate-next":
            num = int(file_name.split('=')[1])+1
            length = str(len(str(num)))
            return ("HTTP/1.1 200 ok\r\nContent-Length: " + length + "\r\n Content-Type: text/plain\r\n\r\n" + str(num)).encode()

        if file_name.split('?')[0] == "calculate-area":
            height = file_name.split('=')[1].split('&')[0]
            width = file_name.split('=')[2]
            num = int(height)*int(width)/2
            length = str(len(str(num)))
            return ("HTTP/1.1 200 ok\r\nContent-Length: " + length + "\r\n Content-Type: text/plain\r\n\r\n" + str(num)).encode()

        ext = file_name.split('.')[1]
        file_data = read_file(file_name, ext)
        length = len(file_data)

        if file_name == "DogBread.jpg" or file_name == "NaziDuck.jpg":
            return b"HTTP/1.1 403 Forbidden\r\n\r\n"
        if file_name == "MovingImage.jpg":
            return b'HTTP/1.1 302 Temporarily Moved' + b'\r\n' + b'Location: Moved/MovingImage.jpg' + b'\r\n\r\n'
        if not os.path.isfile(file_name):
            response = b"HTTP/1.1 404 File Not Found\r\n\r\n"
            if ext != 'txt' or ext != 'css' or ext != 'js' or ext != 'html' or ext != 'jpg':
                return b"HTTP/1.1 500 Internal Server Error\r\n\r\n"
        else:
            if ext == 'html' or 'txt':
                response = "HTTP/1.1 200 ok\r\nContent-Length: " + str(length) + "\r\n Content-Type: text/html; charset=utf-8\r\n\r\n"
            elif ext == 'jpg':
                response = "HTTP/1.1 200 ok\r\nContent-Length: " + str(length) + "\r\n Content-Type: image/jpeg\r\n\r\n"
            elif ext == 'js':
                response = "HTTP/1.1 200 ok\r\nContent-Length: " + str(length) + "\r\n Content-Type: text/javascript; charset=UTF-8\r\n\r\n"
            elif ext == 'css':
                response = "HTTP/1.1 200 ok\r\nContent-Length: " + str(length) + "\r\n Content-Type: text/css\r\n\r\n"
            elif ext == 'calculate-next':
                response = "HTTP/1.1 200 ok\r\nContent-Length: " + str(length) + "\r\n Content-Type: text/plain\r\n\r\n"
            response = response.encode() + file_data
        return response
    else:
        headers = request.split('\r\n')
        SaveFolder = headers[0].split('/')[1]
        with open(SaveFolder + '/' + request.split("'")[-1].split('\r\n\r\n')[0], 'wb') as f:
            f.write(body)
        return b"HTTP/1.1 200 ok\r\n\r\n"



def handle_client(sock, tid, addr):
    print("New Client")
    data = ""
    try:
        request, body = http_rcv(sock)
    except:
        sock.close()
        return
    if request == b'':
        sock.close()
        return
    print("RCV<<<<",request)
    response = build_response(request, body)
    print("Will SEND<<<<", response)
    sock.send(response)
    sock.close()


def main():
    srv_sock = socket.socket()
    srv_sock.bind(('0.0.0.0', 80))
    srv_sock.listen(20)
    srv_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    i = 0
    threads = []
    while True:
        cli_sock, addr = srv_sock.accept()
        t = threading.Thread(target=handle_client, args=(cli_sock, str(i), addr))
        t.start()
        threads.append(t)
        i += 1


if __name__ == '__main__':
    main()