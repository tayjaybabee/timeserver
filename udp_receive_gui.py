#!/bin/python3

# BUGGY Run through another easily killable script or be ready to
# use your task manager.

from argparse import ArgumentParser
from threading import Thread
import os
import sys
import winsound
import socket
from time import sleep
from wakeup import calc, interpret
__version__ = '1.3'

WIN_TITLE = f'Broadcast SniffLer (v{__version__})'

numerical = None


class ArgParser(ArgumentParser):
    def __init__(self):
        super().__init__()
        
        self.add_argument('-m',
                          '--mute',
                          help="Don't play any sound while operating.",
                          action='store_true',
                          required=False,
                          default=False
                          )
        
        self.add_argument(
            '--copy-on-exit',
            help="Copy all the outout to the clipboard on exiting.",
            action='store_true',
            required=False,
            default=False
            )
        
args = ArgParser()
args = args.parse_args()


def install_missing(install_name):
    global numerical

    from os import system
    if not isinstance(install_name, list):
        if isinstance(install_name, str):
            if install_name != 'prompt-toolkit':
                to_install = install_name.replace(' ', '').split(',')
                to_install = install_name.split(',')
            else:
                to_install = ['prompt-toolkit']
        else:
            raise TypeError()
    else:
        to_install = install_name
    if 'prompt-toolkit' in to_install:
        try:
            if len(to_install) != 1:
                if len(to_install) == 2:
                    if not'inspyre-toolbox' and 'prompt-toolkit' in to_install:
                        raise ValueError(to_install)

        except ValueError as e:
            print(
                "Developer Error. Prompt Toolkit must be passed alone or with inspyre-toolbox")
            raise e
    try:
        from inspyre_toolbox.humanize import Numerical
    except ModuleNotFoundError:
        print('Installing inspyre-toolbox')
        system('pip install inspyre_toolbox')
        from inspyre_toolbox.humanize import Numerical

    numerical = Numerical
    num_missing = numerical(len(to_install))
    missing_count = num_missing.count_noun('packages')

    for pkg in to_install:
        print(f"Missing {install_name}, installing...")
        system(f'pip install {pkg}')


missing = []

try:
    from prompt_toolkit.shortcuts import yes_no_dialog
except ImportError as e:
    try:
        install_missing('prompt-toolkit')
        from prompt_toolkit.shortcuts import yes_no_dialog
    except:
        raise


try:
    import PySimpleGUI as psg
except ImportError:
    missing.append('PySimpleGUI')

try:
    from inspyre_toolbox.humanize import Numerical
except ImportError:
    install_missing('inspyre-toolbox')
    
try:
    import pyperclip as cb
except ImportError:
    missing.append('pyperclip')

if len(missing) >= 1:
    num = Numerical(len(missing))
    if yes_no_dialog(f"You are missing {num.count_noun('package')}. Should I install them?"):
        install_missing(missing)

import PySimpleGUI as psg
import pyperclip as cb

muted = args.mute
copy_on_exit = args.copy_on_exit


# Declare our theme choice
psg.theme("DarkAmber")

# Set a buffer var to print from
buffer = None

# A var for the daemonized thread to check if we're running
running = False

# Start a socket object
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)


def get_win_layout():
    """
    Returns the layout object for our PySimpleGUI window

    Returns
    -------
    layout : list
        A list that will act as our layout plot for our window.

    """
    global muted, copy_on_exit

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
            psg.Checkbox(
                'Mute', 
                enable_events=True, 
                key='MUTE_CHECK', 
                default=muted, 
                tooltip="Mute incoming packet ding."
                ),
            psg.VerticalSeparator(),
            psg.Checkbox(
                'Copy on Exit',
                enable_events=True,
                key='COPY_ON_EXIT_CHECK',
                default=copy_on_exit,
                tooltip="Copy the output received upon exiting the program.",
                )
            
        ],
        [
            psg.Button('Quit', enable_events=True, key='QUIT_BTN'),
            psg.Button('Copy to Clipboard', key='COPY_BTN')

        ]

    ]

    return layout


def init(host='', port=5005):
    sock.bind((host, port))
    # optional: set host to this computer's IP address


def receive(buffersize=1024):
    data, addr = sock.recvfrom(buffersize)
    return(data, addr)


def end():
    sock.close()
    
    
def to_cb(vals):
    field = vals['MULTILINE']
    cb.copy(field)
    

def beep():
    """
    Beeps if instance variable 'muted' is not bool(True)

    Returns
    -------
    None.

    """
    global muted
    
    if not muted:
        winsound.Beep(1500, 60)
        


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
            beep()
            batt_data = data[4:40]
            batt_data_first35 = batt_data[0:35]
            received_crc = batt_data[35]
            calculated_crc = calc(batt_data_first35)
            (voltage, current, power, highcell, lowcell, difference, percent, temperatures) = interpret(data[4:40])
            msg = ""
            if received_crc == calculated_crc:
                msg = str(f"From{str(' ' * 12)}{addr} \nRecv Port: \
{recvport} \nBytes:{str(' ' * 10)}{len(data)} \nData: {data}\n\
{voltage}V, {current}A, {power}W, Highcell: {highcell}V, Lowcell: \
{lowcell}V, Difference: {difference}V, {percent}% charged, Temperatures: {temperatures}")
            else:
                msg = str(f"From{str(' ') * 12}{addr} \nRecv Port: \
{recvport} \nBytes:{str(' ' * 10)}{len(data)} \nData: {data}\n\
CRC doesn't match, expected: {hex(calculated_crc)} got {hex(received_crc)}")
            buffer = msg

    end()


def safe_exit(window, values=None):
    """
    Just as implied, exits the program safely.

    Exits the program safely, killing the daemonized thread by assigning
    bool(False) to 'running'

    Returns
    -------
    None.

    """
    global running, copy_on_exit
    print("Exiting per user request.")
    running = False
    if copy_on_exit and values is not None:
        to_cb(values)
        
    if not window.was_closed():
        window.close()
        
    sys.exit()


def main():
    global buffer, muted, copy_on_exit

    # Configure our window, first a title for it

    # Then declare and instantiate the actual window object
    win = psg.Window(
        WIN_TITLE,
        layout=get_win_layout(),
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
    
    last_copy_check = None

    # Start our GUI loop.
    while True:
        event, values = win.Read(timeout=100)

        # If the 'X' button is pressed;
        if event is None:
            print('User exited')
            safe_exit(win, values)
            break

        # If the 'Quit' button is pressed;
        if event == 'QUIT_BTN':
            print('User hit "Quit" button')
            safe_exit(win, values)
            break
        
        
        if event == 'MUTE_CHECK':
            muted = values['MUTE_CHECK']
            
        
        if event == 'COPY_BTN':
            to_cb(values)
            
        
        if event == 'COPY_ON_EXIT_CHECK':
            copy_on_exit = values['COPY_ON_EXIT_CHECK']
            
        if values['COPY_ON_EXIT_CHECK']:
            copy_on_exit = True
        else:
            copy_on_exit = False
        
        if not last_copy_check == copy_on_exit:
            vis = not copy_on_exit
            win['COPY_BTN'].update(visible=vis)
            
        last_copy_check = copy_on_exit
            

        # If the buffer is different than the cached buffer;
        if buffer != last_read:
            counter += 1
            count = Numerical(counter)
            out = str('-' * 15) + ' Packet #' + count.commify() + \
                '\n' + buffer + '\n' + str('-' * 15)
            win['MULTILINE'].print(out + '\n')
            last_read = buffer
            
if __name__ == "__main__":
    main()
