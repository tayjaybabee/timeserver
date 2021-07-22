#!/bin/python3

# BUGGY Run through another easily killable script or be ready to
# use your task manager.

__version__ = '1.0'

import socket
import winsound
import PySimpleGUI as psg
import sys
import os

from threading import Thread

# Declare our theme choice
psg.theme("DarkAmber")

# Set a buffer var to print from
buffer = None

# A var for the daemonized thread to check if we're running
running = False

# The layout for the window
layout = [
    [
        psg.Text('Incoming packets:')

    ],

    [
        psg.Multiline(
            'Starting output\n\n\n',
            size=(100, 50),
            key='MULTILINE',
            reroute_cprint=True,
            reroute_stdout=True,
            reroute_stderr=True,
            auto_refresh=True,

        )
    ],
    [
        psg.Button('Quit', enable_events=True, key='QUIT_BTN'),
        psg.Button('Copy to Clipboard', disabled=True, key='COPY_BTN')

    ]

]


# Start a socket object
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)


def init(host='', port=5005):
    sock.bind((host, port))
    # optional: set host to this computer's IP address


def receive(buffersize=1024):
    data, addr = sock.recvfrom(buffersize)
    return(data, addr)


def end():
    sock.close()


# A function to target with our thread spawner.
def listener():
    """
    Listens for UDP broadcast traffic as long as 'running' is bool(True)

    Returns
    -------
    None.

    """
    global buffer, running

    recvport = 5606

    # Indicate that we are indeed running
    running = True

    while running:

        try:
            init(port=recvport)
            okay = True
        except:
            print(f'Port {recvport} is already open by another application. \
    Aborting.')
            okay = False
            sys.exit()
        while okay:
            if not running:
                okay = False
                sys.exit()
            data, addr = receive()
            winsound.Beep(1500, 60)
            msg = str(f"From{str(' ' * 12)}{addr} \nRecv Port: \
    {recvport} \nBytes:{str(' ' * 10)}{len(data)} \nData: {data}")

            buffer = msg

    end()


def safe_exit():
    """
    Just as implied, exits the program safely.

    Exits the program safely, killing the daemonized thread by assigning
    bool(False) to 'running'

    Returns
    -------
    None.

    """
    global running
    print("Exiting per user request.")
    running = False
    sys.exit()


def main():
    global buffer

    # Configure our window, first a title for it
    win_title = f'Broadcast SniffLer (v{__version__})'

    # Then declare and instantiate the actual window object
    win = psg.Window(
        win_title,
        layout=layout,
        finalize=True,
        resizable=True, size=(900, 900)

    )

    # Before we start our window let's declare the listener thread
    listen = Thread(target=listener, daemon=True)

    # Then start it. Since it's daemonized and listening to the status of
    # 'running' we don't have to worry about '.join'ing later
    listen.start()

    # Let's set up a cache variable so our GUI will have a reference to decide
    # when one read is different from it's last
    last_read = None

    counter = 0

    # Start our GUI loop.
    while True:
        event, values = win.Read(timeout=100)

        # If the 'X' button is pressed;
        if event is None:
            win.close()
            print('User exited')
            safe_exit()
            break

        # If the 'Quit' button is pressed;
        if event == 'QUIT_BTN':
            win.close()
            print('User hit "Quit" button')
            safe_exit()
            break

        # If the buffer is different than the cached buffer;
        if buffer != last_read:
            counter += 1
            out = str('-' * 15) + ' Packet #' + str(counter) + \
                '\n' + buffer + '\n' + str('-' * 15)
            win['MULTILINE'].print(out + '\n')
            last_read = buffer


if __name__ == "__main__":
    main()
