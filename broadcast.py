from time import sleep, time
import socket

def main():
    host = '192.168.1.255'
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((host,0))
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

    while True:
        t = bytes(str(time()), 'utf-8')
        print(f'sending packet {t}')
        sock.sendto(t,("192.168.1.255", 5005))
        sleep(2.0)
    sock.close()

main()
