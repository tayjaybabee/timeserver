from time import sleep, time
import serial  # python3 -m pip install pyserial
from udp_send import init, send, end, time_32bits

wakeup_string = b"\x3A\x13\x01\x16\x79"


def about_bytestring(wakeup_string):
    print(type(wakeup_string))
    print(len(wakeup_string))
    print(wakeup_string)


def interpret(bytestring):
    intarray = []
    for byte in bytestring:
        intarray.append(byte)
    if len(intarray) == 36:
        # voltage = (intarray[22] * 256 + intarray[21]) / 1000.0
        # voltage = np.array([intarray[22],intarray[21]], dtype=np.int16)
        voltage = int. from_bytes([intarray[21], intarray[22]],
                                  byteorder="little", signed=False) / 1000.0
        current = int. from_bytes([intarray[25], intarray[26]],
                                  byteorder="little", signed=True) / 1000.0
        highcell = int. from_bytes([intarray[29], intarray[30]],
                                   byteorder="little", signed=False) / 1000.0
        lowcell = int. from_bytes([intarray[31], intarray[32]],
                                  byteorder="little", signed=False) / 1000.0
        percent = intarray[5]
        temperature1 = intarray[7]
        temperature2 = intarray[8]
        temperature3 = intarray[9]
        temperature4 = intarray[10]
        power = round(voltage * current, 4)
        chargedischarge = ""
        if current == 0:
            chargedischarge = ". "
        else:
            if current > 0:
                chargedischarge = " (charging). "
            else:
                chargedischarge = " (discharging). "

        difference = round(highcell - lowcell, 4)
        print(f"{voltage}V {current}A{chargedischarge}{power}W \
Cell with highest voltage at {highcell}V, lowest: {lowcell}V Difference: \
{difference}V {percent}% charged Temperatures: {temperature1}°C {temperature2}\
°C {temperature3}°C {temperature4}°C")
    else:
        print(f"bytes: {len(bytestring)} Data: {bytestring}")


def main():
    # about_bytestring(wakeup_string)
    ser = serial.Serial(
        port="/dev/ttyS0",
        baudrate=9600,
        timeout=4.0
    )

    dest = '192.168.1.255'
    init()  # initialize UDP broadcast
    while True:
        last_writetime = time()
        ser.write(wakeup_string)
        serstring = ser.read(size=36)
        interpret(serstring)
        if len(serstring) == 36:
            packet = time_32bits(timestamp=last_writetime) + serstring +\
                     b' ' + bytes(str(round(last_writetime, 3)), 'utf-8')
            send(packet=packet, dest=dest, port=5606)

        secondselapsed = time() - last_writetime
        if secondselapsed > 0:
            if secondselapsed < 5.0:
                sleep(5.0 - secondselapsed)
                # print(f"   elapsed time before sleep: {secondselapsed},\
                # after sleep: {time() - last_writetime}")
            else:
                print(f"   elapsed time: {secondselapsed}")
        else:
            print(f"   time counting backwards? seconds elapsed: \
{secondselapsed}")
            break

    print("closing serial port")
    ser.close()  # close serial port
    end()        # close UDP port


if __name__ == "__main__":
    main()
