import socket
import json


class Network:
    def __init__(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server = "192.168.0.15"
        self.port = 5555
        self.addr = (self.server, self.port)
        self.p = self.connect()

    def getP(self):
        return self.p

    def connect(self):
        # When we connect, we send validation token back to a client
        # self.p will have 'Connected'
        try:
            self.client.connect(self.addr)
            return json.loads(self.client.recv(2048))  # decompose objects' data / load bytes data
        except:
            pass

    def send(self, data):
        try:
            self.client.send(json.dumps(data))    # dump into a pickle object to send
            return json.loads(self.client.recv(2048))
        except socket.error as e:
            print(e)

from _thread import *
import fog_of_war as fow
from queue import Queue

server = "127.0.0.1"
port = 5555

# setting up a connection
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# bind server and port to socket, check if port is being used
try:
    s.bind((server, port))
except socket.error as e:
    str(e)

# open up the port, and have multiple clients connect
# blank means unlimited connection
s.listen(2)
print("Waiting for a connection, server started")

game:Queue[fow.BoardPacket] = Queue()
game.put(fow.FOWChess.new_game())

def threaded_client(conn, player:bool):
    message = game.get(-1).create_board_packet(player).__dict__()
    conn.send(json.dumps(message).encode('utf-8'))    # dump into a pickle object to send
    while True:
        try:
            if player is game[-1].current_turn:
                data = json.loads(conn.recv(9000))  # 2048 = amount of bits/information
                game.put(game[-1].from_fow(fow.Move.from_json(data)))
                if not data:
                    print("Disconnected")
                    break

        except:
            break

    print("Lost connection")
    conn.close()


currentPlayer = 0

while True:
    # conn = type of object connected, addr = IP Address
    s.listen()
    conn, addr = s.accept()
    print("Connected to:", addr)

    start_new_thread(threaded_client, (conn, currentPlayer))
    currentPlayer += 1