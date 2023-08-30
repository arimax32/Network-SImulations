import socket
import threading
import time
import random

IP = socket.gethostbyname(socket.gethostname())
PORT = 4452
ADDR = (IP, PORT)
FORMAT = "utf-8"
HEADERSIZE = 10
IPMASK = "192.168.1."
IP_POOL = []
free = {}
allocated = {}
clients = []
N = 0

def generateIp():
    for i in range(0,256,5):
        ip = IPMASK + str(random.randint(i,min(255,i+5)))
        global IP_POOL
        IP_POOL.append(ip)
        global free
        free[ip] = True

    random.shuffle(IP_POOL)

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


def handle_client(client,lock):
    while True:
        message = receive_message(client)
        global N 
        if message == "0":
            lock.acquire()
            N = N + 1
            free[allocated[client]] = True
            print(f"IP : {allocated[client]} got leased out and is now free\n")
            allocated[client] = None
            lock.release()
        elif not message:
            lock.acquire()
            N = N + 1
            free[allocated[client]] = True
            index = clients.index(client)
            print(f"Client got disconnected and IP : {allocated[client]} is now free\n")
            allocated[client] = None
            clients.remove(client)
            client.close()
            lock.release()
            break
        elif N > 0 :
            ip = ""
            lock.acquire()
            N -= 1
            for ipp in IP_POOL:
                if free[ipp]:
                    ip = ipp
                    break
            lock.release()
            client.send(createFrame(ip).encode(FORMAT))
            lock.acquire()
            allocated[client] = ip
            free[ip] = False
            print(f"IP : {ip} has been Allocated to a Client\n")
            lock.release()
        else:
            client.send(createFrame("0").encode(FORMAT))



def main():
    generateIp()
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(ADDR)
    server.listen()
    global N
    N = int(input('Enter Capacity of DHCP Server : '))
    lock = threading.Lock()
    while True:
        client, address = server.accept()
        if N > 0:
            clients.append(client)
            ip = ""
            N -= 1
            for ipp in IP_POOL:
                if free[ipp]:
                    ip = ipp
                    break
            client.send(createFrame(ip).encode(FORMAT))
            allocated[client] = ip
            free[ip] = False
            print(f"IP : {ip} has been Allocated to a Client\n")
            thread = threading.Thread(target=handle_client, args=(client,lock))
            thread.start()
        else:
            client.send(createFrame("0").encode(FORMAT))



if __name__ == "__main__":
    main()