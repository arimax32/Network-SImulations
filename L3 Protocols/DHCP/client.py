import threading
import socket
import time

IP = socket.gethostbyname(socket.gethostname())
PORT = 4452
ADDR = (IP, PORT)
FORMAT = "utf-8"
HEADERSIZE = 10
LEASE_TIME = 10


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
        message = receive_message(client)
        if not message  or  message == "0":
            print("Can't Connect to the DHCP Server\n")
            client.close()
            break
        else:
            print(f"Client Online IP : {message}")
            time.sleep(LEASE_TIME)
            client.send(createFrame("0").encode(FORMAT))
            print("Client Offline\n")
            time.sleep(2)
            print("IP Renewal Request Sent")
            client.send(createFrame("1").encode(FORMAT))


def main():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(ADDR)
    clientStart(client)

if __name__ == "__main__":
    main()