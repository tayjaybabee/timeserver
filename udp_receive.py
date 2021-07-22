#!/bin/python3

import socket
import winsound


def init(host='', port=5005):
    sock.bind((host, port))
    # optional: set host to this computer's IP address


def receive(buffersize=1024):
    data, addr = sock.recvfrom(buffersize)
    return(data, addr)


def end():
    sock.close()


def main():
    recvport = 5606
    try:
        init(port=recvport)
        okay = True
    except:
        print(f'Port {recvport} is already open by another application. \
Aborting.')
        okay = False
    while okay:
        data, addr = receive()
        winsound.Beep(1500, 60)
        print(f"From {addr} Recv Port: \
{recvport} Bytes: {len(data)} Data: {data}")

    end()


sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

if __name__ == "__main__":
    main()
