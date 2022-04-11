import socket
import threading
import time
import select
import sys
import random
import datetime
import os

HEADER = 64
FORMAT = "utf-8"
DISCONNECT_MESSAGE = "!DISCONNECT"
PORT = 2568
SERVER = socket.gethostbyname(socket.gethostname()) #SERVER = "192.168.0.16"  
ADDR = (SERVER, PORT) #LocalHost
print("[SERVER] Running on " + socket.gethostname() + " At " + SERVER)

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(ADDR)

dir_path = os.path.dirname(os.path.realpath(__file__))

msg = ''
connsDic = {}
# connsList = []
buffer_size = 0

def subDir(path):
    path = path.split('\\')
    del path[-1]
    finalString = ''
    first = True
    for item in path:
        if first:
            first = not first
        else:
            finalString += '\\'
        finalString += item
    return finalString

def upDir(path, newLocation):
    path += f'\\{newLocation}'
    return path

def writetofile():
    global connsDic, connsList
    # f = open('clients.txt', 'a+')
    # f = open('clients.txt', 'a+')
    # f.truncate(0)
    # f.close()
    oldDic = {}
    # print(f'the keys {connsDic.keys()}')
    while True:
        if oldDic != list(connsDic.keys()):
            # print('dics different')
            clients = []
            first = True
            for i in connsDic.keys():
                if not connsDic[i][1]:
                    clients.append(i)

            # print(f'Dics different\n{oldDic} {list(connsDic.keys())}')

            # f = open('clients.txt', 'a+')
            # f.truncate(0)
            # f.write(clients)
            # f.flush()
            # f.close()

            clientsString = 'users '

            for i in clients:
                clientsString += f'{str(i)} '

            clientsString = clientsString[:-1]

            for i in connsDic.keys():
                if connsDic[i][1]:
                    print(connsDic[i])
                    print('Updated Clients list for admins...')
                    print(clientsString)
                    connsDic[i][0][0].send(clientsString.encode(FORMAT))

            oldDic = list(connsDic.keys())

requestedFrom = ''

def recvData(conn, urId):
    global msg, connsDic, connsList, dir_path
    while True:
        # print(urId)
        try:
            msg = conn.recv(1024).decode(FORMAT)
            if msg.startswith('screenshot'):
                msg += f' {urId}'
        except:
            print(f"[{connsDic[urId][0][1]}] ID:{urId} Disconnected")
            if len(connsDic) == 1:
                connsDic = {}
            else:
                del connsDic[urId]
            sys.exit()
        print(f'Received information! --> {msg}')
        # print(msg)
        if msg.startswith(DISCONNECT_MESSAGE):
            daId = msg.split(' ')[-1]
            print(f"[{connsDic[daId][0][1]}] Disconnected")
            connsDic[daId][0][0].close()
            del connsDic[daId]
            sys.exit()
        
        if msg == 'SENDING':
            conn.send('h'.encode(FORMAT)) #acts weird when receiving twice in a row
            fileInfo = conn.recv(buffer_size)
            # newDir = upDir(subDir(dir_path), 'screenshots')
            # if not os.path.exists(f'{newDir}/{urId}'):
            #     os.makedirs(f'{newDir}/{urId}')
            
            # print(f'type of file {type(fileInfo)}')

            # myfile = open(f'{upDir(newDir, urId)}/' + str(datetime.datetime.now()).replace(':', "'") + '.png', 'wb')
            # myfile.write(fileInfo)
            # myfile.close()

            time.sleep(0.2)
            print(requestedFrom)
            if requestedFrom in connsDic.keys():
                print('sending')
                connsDic[requestedFrom][0][0].send(f'SIZE {buffer_size}'.encode(FORMAT))
                time.sleep(0.2)
                connsDic[requestedFrom][0][0].send('SENDING'.encode(FORMAT))
                time.sleep(0.2)
                connsDic[requestedFrom][0][0].sendall(fileInfo)



# requestImage = False

def handle_client():
    global requestImage, msg, connsDic, connsList, buffer_size, happened, changed, requestedFrom

    connected = True
    while connected:
        if msg:
            print(f'Message--> {msg}')

            if msg.startswith('screenshot'):
                # requestImage = True
                clientId = msg.split(' ')[1]
                requestedFrom = msg.split(' ')[-1]
                if clientId in connsDic.keys():
                    print(f"Request Received from {connsDic[clientId][0][1]} ID: {clientId} for {connsDic[requestedFrom][0][1]} ID: {requestedFrom}")
                    connsDic[clientId][0][0].send('SENDIMAGE'.encode(FORMAT))
                    print('sent "SENDIMAGE"')
                else:
                    print(f'Requested client ID: {clientId} not found (offline)')

            if msg.startswith('shutdown'):
                clientId = msg.split(' ')[-1]
                if clientId in connsDic.keys():
                    print(f"Request Received for {connsDic[clientId][0][1]} ID: {clientId}")
                    connsDic[clientId][0][0].send('GOAWAY'.encode(FORMAT))
                else:
                    print(f'Requested client ID: {clientId} not found (offline)')

            if msg.startswith('SIZE'):
                buffer_size = int(msg.split(' ')[-1])

            msg = ''

def start():
    global connsDic, connsList

    handleThread = threading.Thread(target = handle_client, args =())
    handleThread.start()
    writeFile = threading.Thread(target = writetofile, args =())
    writeFile.start()

    server.listen()
    while True:
        # print(connsDic)
        # print(connsList)
        conn, addr = server.accept()
        msg = conn.recv(1024).decode(FORMAT)
        if msg.startswith('ADMIN'):
            daId = msg.split(' ')[-1]
            connsDic[daId] = [[conn, addr], True]
            print(f"[NEW CONNECTION] {addr} |ADMIN| connected --> ID:{daId}")
        elif msg.startswith('CLIENT'):
            daId = msg.split(' ')[-1]
            connsDic[daId] = [[conn, addr], False]
            print(f"[NEW CONNECTION] {addr} |CLIENT| connected --> ID:{daId}")
        
        # connsList.append(conn)

        recvthread = threading.Thread(target = recvData, args = (conn, daId))
        recvthread.start()

        print(f"[ACTIVE THREADS] {threading.activeCount()}")

print("[SERVER] Server Starting...")

start()