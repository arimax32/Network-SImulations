import socket
import threading
import time
import random

IP = socket.gethostbyname(socket.gethostname())
PORT = 4453
ADDR = (IP, PORT)
FORMAT = "utf-8"
HEADERSIZE = 10
IPMASK = "192.168.1."
BROADCAST = "FF.FF.FF.FF"
MAC_DATABASE = ["00-04-3A-5F-66-3A","01-34-47-55-3B-3A","00-24-5A-6C-56-3A","00-05-3D-2A-33-5A"]
ClientMap = {}
clients = []

def receive_message(client_socket):
    try:
        msg_header = client_socket.recv(HEADERSIZE)

        if not len(msg_header):
            return False

        msg_len = int(msg_header.decode(FORMAT).strip())

        data = client_socket.recv(msg_len).decode(FORMAT)
        return data

    except:
        return False

def createFrame(message):
    return  f"{len(message):<{HEADERSIZE}}" + message

def broadcast(message,node):
    for client in clients:
        if client == node:
            continue
        client.send(message)

def handle_client(client):
    while True:
        try:
            message = receive_message(client)
            packet = message.split('$')
            if packet[-1] == BROADCAST:
                broadcast(createFrame(message).encode(FORMAT),client)
            else:
                unicast_ip = packet[-1]
                ClientMap[unicast_ip].send(createFrame(message).encode(FORMAT))
        except:
            index = clients.index(client)
            clients.remove(client)
            client.close()
            break

def StartNetwork():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(ADDR)
    server.listen()
    num = 0
    print('Network is ready to Start ...')
    while True:
        client, address = server.accept()
        num += 1
        IP = IPMASK + str(num)
        MAC = MAC_DATABASE[num-1]
        print(f'Connection Established with Client {num}, IP : {IP}')
        clients.append(client)
        ClientMap[IP] = client
        client.send(createFrame(f'IP : {IP} ,  MAC : {MAC} is Connected to  the Network\n').encode(FORMAT))
        thread = threading.Thread(target=handle_client, args=(client,))
        thread.start()



if __name__ == "__main__":
    StartNetwork()