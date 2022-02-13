#!/bin/python3

import socket
# import winsound
from wakeup import interpret, calc
from colorama import init


def udpinit(host='', port=5005):
    sock.bind((host, port))
    # optional: set host to this computer's IP address


def receive(buffersize=1024):
    data, addr = sock.recvfrom(buffersize)
    return(data, addr)


def end():
    sock.close()


def main():
    init()  # Enable ANSI color in the terminal if running from Windows
    recvport = 5606
    try:
        udpinit(port=recvport)
        okay = True
    except:
        print(f'Port {recvport} is already open by another application. \
Aborting.')
        okay = False
    prev_batt_data_hex = ''
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
            avgtemp = (temperatures[0] + temperatures[1] +
                       temperatures[2] + temperatures[3]) / 4.0
            # batt_data_hex = batt_data.hex()
            pos = 0
            for byte in batt_data:
                byte_hex = hex(byte)[2:].zfill(2).upper()
                if pos == 5:
                    print(f"\033[33m{byte_hex}\033[00m", end='')     # print % byte in yellow
                elif (pos > 6 and pos < 11):
                    print(f"\033[32m{byte_hex}\033[00m", end='')     # print temperature bytes in green
                elif (pos > 24 and pos < 29):
                    print(f"\033[31m{byte_hex}\033[00m", end='')     # print current bytes in red
                elif (pos > 20 and pos < 25):
                    print(f"\033[36m{byte_hex}\033[00m", end='')     # print voltage bytes in cyan
                elif (pos > 28 and pos < 33):
                    print(f"\033[35m{byte_hex}\033[00m", end='')     # print cell hi/lo voltage bytes in magenta
                elif pos == 35:
                    print(f"\033[30;01m{byte_hex}\033[00m", end='')  # print crc in dark grey
                else:
                    if (len(prev_batt_data_hex) > 71 and byte_hex == prev_batt_data_hex[pos * 2:(pos * 2) + 2]):
                        print(byte_hex, end='')                          # print unknown bytes without formatting
                    else:                                                # invert foreground/background if an
                        print(f"\033[30;47m{byte_hex}\033[00m", end='')  # unknown byte differs from previous packet
                pos += 1
            prev_batt_data_hex = batt_data.hex().zfill(72).upper()
            print("\033[33m{}\033[00m" .format(" " + str(percent) + "% "), end='')
            print(f"\033[32m{round(avgtemp, 2)}°C \033[00m", end='')
            print(f"\033[32m{round((avgtemp * 1.8) + 32.0, 1)}°F \033[00m", end='')
            print(f"\033[35mlo {round(lowcell, 3)}V \033[00m", end='')
            print(f"\033[36m{round(voltage, 3)}V \033[00m", end='')
            print(f"\033[35mhi {round(highcell, 3)}V \033[00m", end='')
            print(f"\033[31m{round(current, 3)}A \033[00m", end='')
            print(f"{round(power, 1)}W", end='')
            print('')                                                # new line
            # print(prev_batt_data_hex)
        else:
            print(f"CRC doesn't match. expected: {hex(calculated_crc)} got \
{hex(received_crc)}")

    end()


sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

if __name__ == "__main__":
    main()
