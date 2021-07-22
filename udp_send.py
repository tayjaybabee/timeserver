#!/bin/python3

from time import sleep, time
import socket


def init(host=''):
    sock.bind((host, 0))
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    # optional: set host to this computer's IP address


def send(packet=b'', dest='192.168.1.255', port=5005):
    sock.sendto(packet, (dest, port))
    # set dest to the destination IP address or to broadcast set to your
    # subnet's broadcast address such as '192.168.1.255'   In Linux, the
    # command "ip a" tells you the broadcast address.


def end():
    sock.close()


def time_32bits(timestamp=1626809049):
    epochshift = int(365.25 * 70)
    epochshift_seconds = epochshift * 24 * 60 * 60
    timestamp = int(epochshift_seconds + timestamp)
    binary = int.to_bytes(timestamp, 4, 'big', signed=False)
    return(binary)
    # Time protocol is unsigned  32-bit  integer number of seconds since
    # midnight Jan 1 1900 served on TCP port 37 upon opening TCP session
    # The difference between  Unix time  and  Time protocol is 70 years;
    # take into account 1 extra day each leap year between 1900 and 1970
    # number of seconds elapsed between midnight  1/1/1900 UTC  and mid-
    # night 1/1/1970 UTC. Last date/time that can be represented as this
    # 32-bit  unsigned int is:  Thursday   Feb 7, 2036   12:28:15 AM  or
    # 4294967295 (hex value 0xFFFFFFFF)


def main():
    init()
    while True:
        t = time()
        t_32 = time_32bits(timestamp=t)
        batterypacket = b"\x00\x00\x00\x00\x00\x00\x00\x00\
\x00\x00\x00\x00\x00\x00\x00\x00\
\x00\x00\x00\x00\x00\x00\x00\x00\
\x00\x00\x00\x00\x00\x00\x00\x00\
\x00\x00\x00\x00 "
        packet = t_32 + batterypacket + bytes(str(round(t, 3)), 'utf-8')
        print(f'Sending packet: {packet}')
        send(packet=packet, dest='192.168.1.255', port=5606)
        sleep(5.0)
    end()
    # If you want to see an example  of how to use the functions in this
    # .py file,  run it standalone and this main() function will run and
    # as an example transmit the number of seconds since 1900 UTC in the
    # form of 4-byte (32-bit) unsigned integer,  then 36 more bytes as a
    # placeholder for battery status, then the same time in UTF-8 format
    # (really it's ASCII) - the same time but with millisecond precision
    # in the form of number of seconds since midnight 1/1/1970 UTC.


sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

if __name__ == "__main__":
    main()
