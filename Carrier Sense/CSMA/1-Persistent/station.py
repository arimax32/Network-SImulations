import socket
import time

IP = socket.gethostbyname(socket.gethostname())
PORT = 4456
ADDR = (IP, PORT)
HEADERSIZE = 10
FORMAT = "utf-8"

def receive_message(client_socket):
    try:
        msg_header = client_socket.recv(HEADERSIZE)

        if not len(msg_header):
            return False

        msg_len = int(msg_header.decode('utf-8').strip())

        data = client_socket.recv(msg_len).decode(FORMAT)
        return data

    except:
        return False

def createFrame(message):
    return  f"{len(message):<{HEADERSIZE}}" + message

def main():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(ADDR)
    print(f"[CONNECTED] Station connected to SHARED CHANNEL at {IP}:{PORT}")

    res = receive_message(client).split("$")
    n = int(res[0])
    client_num = int(res[1])
    print(f"There are {n} stations in the Shared Channel")
    print(f"You are Station  {client_num + 1}\n")

    while True:
        dest_client = int(input("Enter Station to send data : "))
        if dest_client - 1  == client_num : 
            print("Invalid Destination")
            continue
        data = input(f"\nEnter Data to be sent to Station {dest_client} : ")
        if data == "exit":
            break
        res = "0"
        exit = False
        while res == "0":
            print("Sensing Channel\n")
            client.send(createFrame(str(dest_client - 1) + data + "1").encode(FORMAT))
            res = receive_message(client)
            if not res: 
                print("Channel Destroyed")
                exit  = True
                break 

            if res == "0" : 
                print("Channel is Busy")
            else:
                print("Channel Idle, Packet Sent")

        if exit:
            break

        print("\n")


    client.close()


if __name__ == "__main__":
    main()