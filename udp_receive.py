#!/bin/python3

import socket
import winsound
from wakeup import interpret, calc


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
        # winsound.Beep(1500, 60) // this gets annoying
        batt_data = data[4:40]
        batt_data_first35 = batt_data[0:35]
        received_crc = batt_data[35]
        calculated_crc = calc(batt_data_first35)
        if received_crc == calculated_crc:
            # print(f"From {addr} Recv Port: {recvport} Bytes: {len(data)}")
            (voltage, current, power, highcell, lowcell, difference, percent,
             temperatures) = interpret(batt_data)
            avgtemp = (temperatures[0] + temperatures[1] + temperatures[2] + temperatures[3]) / 4.0
            # batt_data_hex = batt_data.hex()
            pos = 0
            for byte in batt_data:
                byte_hex = hex(byte)[2:].zfill(2)
                if pos == 5:
                    print("\033[93m{}\033[00m" .format(byte_hex), end='')  # print % byte in yellow
                elif (pos > 6 and pos < 11):
                    print("\033[92m{}\033[00m" .format(byte_hex), end='')  # print temperature bytes in green
                elif (pos > 24 and pos < 27):
                    print("\033[91m{}\033[00m" .format(byte_hex), end='')  # print current bytes in red
                elif (pos > 20 and pos < 23):
                    print("\033[96m{}\033[00m" .format(byte_hex), end='')  # print voltage bytes in cyan
                elif (pos > 28 and pos < 33):
                    print("\033[95m{}\033[00m" .format(byte_hex), end='')  # print cell hi/lo voltage bytes in purple
                elif (pos == 35):
                    print("\033[90m{}\033[00m" .format(byte_hex), end='')  # print crc in gray
                else:
                    print(byte_hex, end='')                                # print unknown bytes as plain colored text
                pos += 1
            print("\033[93m{}\033[00m" .format(" " + str(percent) + "% "), end='')
            print("\033[92m{}\033[00m" .format(str(avgtemp) + "°C "), end='')
            print("\033[95m{}\033[00m" .format("lo " + str(lowcell) + "V "), end='')
            print("\033[96m{}\033[00m" .format(str(voltage) + "V "), end='')
            print("\033[95m{}\033[00m" .format("hi " + str(highcell) + "V "), end='')
            print("\033[91m{}\033[00m" .format(str(current) + "A "), end='')
            print(str(power) + "W", end='')
            print('')                                                      # new line
        else:
            print(f"CRC doesn't match. expected: {hex(calculated_crc)} got \
{hex(received_crc)}")

    end()


sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

if __name__ == "__main__":
    main()
