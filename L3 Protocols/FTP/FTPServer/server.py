import socket
import threading
import time
import random

IP = socket.gethostbyname(socket.gethostname())
PORT = 4454
ADDR = (IP, PORT)
FORMAT = "utf-8"
HEADERSIZE = 10
clients = []
file = ["serverfile1.txt","serverfile2.txt"]

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


def handle_client(client,n,lock):
    while True:
        message = receive_message(client)
        if not message : 
            clients.remove(client)
            client.close()
            print(f"\nClient {n} Disconnected")
            break
        if message == "LIST":
            lock.acquire()
            data = "Files in the Server :- \n"
            for fi in file:
                data += fi + "\n"
            lock.release()
            client.send(createFrame(data).encode(FORMAT))
        elif message[0] == "$":
            lock.acquire()
            msg = message.split("$")
            FILENAME = msg[1]
            print(f"File Received from Client {n} , Saved as {FILENAME}\n")
            with open(FILENAME, 'w') as f:
                f.write(msg[2])
            file.append(FILENAME)
            lock.release()
        else:
            msg =""
            if message in file:
                fp = open(message,'r')
                msg = fp.read()
            else:
                msg = "$File doesn't exist\n"
            client.send(createFrame(msg).encode(FORMAT))


def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(ADDR)
    server.listen()
    num = 0
    lock = threading.Lock()
    while True:
        client, address = server.accept()
        clients.append(client)
        num += 1
        print(f"Client {num} Connected , {address}")
        thread = threading.Thread(target=handle_client, args=(client,num,lock))
        thread.start()



if __name__ == "__main__":
    main()