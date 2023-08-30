import threading
import socket

IP = socket.gethostbyname(socket.gethostname())
PORT = 4453
ADDR = (IP, PORT)
FORMAT = "utf-8"
HEADERSIZE = 10
IP = ""
MAC = ""
BROADCAST = "FF.FF.FF.FF"


client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(ADDR)

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

def getip(msg):
    i = msg.index(',')
    return msg[5:i].strip()

def getmac(msg):
    i = msg.index('M')
    j = msg.index('is')
    return msg[i+5:j].strip()

def createFrame(message):
    return  f"{len(message):<{HEADERSIZE}}" + message

def client_receive():
    while True:
        try:
            message = receive_message(client)
            packet = message.split('$')
            if len(packet) == 1:
                print("\n" + message)
                if message[:2] == "IP":
                    global IP
                    IP = getip(message)
                    global MAC
                    MAC = getmac(message)

            elif packet[-1] == BROADCAST:
                if packet[1] == IP :
                    message = IP + '$' + MAC + '$' + packet[2] + '$' + packet[0]
                    print("UNICAST Message sent\n")
                    client.send(createFrame(message).encode(FORMAT))
                else:
                    print("\nPacket Rejected")
            else:
                print(f"MAC : {packet[1]} received for IP : {packet[0]}\n")

        except:
            print('Error!')
            client.close()
            break


def client_send():
    while True:
        dstip = input("")
        message = IP + '$' + dstip + '$' + MAC + '$' + BROADCAST
        print("BROADCAST Message sent")
        client.send(createFrame(message).encode(FORMAT))



receive_thread = threading.Thread(target=client_receive)
receive_thread.start()

send_thread = threading.Thread(target=client_send)
send_thread.start()