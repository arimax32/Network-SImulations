import threading
import socket
import os

IP = socket.gethostbyname(socket.gethostname())
PORT = 4449
ADDR = (IP, PORT)
FORMAT = "utf-8"
HEADERSIZE = 10


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

def clientStart(client):
    while True:
        domain = input("Enter Domain Name : ")
        if domain =="exit":
            client.close()
            break
        client.send(createFrame(domain).encode(FORMAT))
        res = receive_message(client)
        if not res:
            prnt("Disconnected")
            break
        print(res + "\n")

def main():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(ADDR)
    clientStart(client)

if __name__ == "__main__":
    main()