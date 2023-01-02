import socket
import time
import threading


def protocol_build_request(file_name):
    with open(file_name, 'rb') as f:
        body = f.read()
        length = len(body)
        response = f"POST /uploads/ HTTP/1.1\r\nContent-Length: {length}\r\nContent-Disposition: attachment; filename*=UTF-8'{file_name.split('/')[-1:][0]}\r\n\r\n"
    return response.encode() + body


def main(ip):
    port = 80
    while True:
        sock = socket.socket()
        try:
            sock.connect((ip, port))
            print(f'Connect succeeded {ip}:{port}')
        except:
            print(f'Error while trying to connect.  Check ip or port -- {ip}:{port}')

        image_path = input("enter an image you want to send: ")
        to_send = protocol_build_request(image_path)
        sock.send(to_send)


if __name__ == '__main__':
    main("127.0.0.1")