import socket

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

        msg_len = int(msg_header.decode(FORMAT).strip())

        data = client_socket.recv(msg_len).decode(FORMAT)
        return data

    except:
        return False


def main():
    receiver = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    receiver.connect(ADDR)

    client = receive_message(receiver)
    client = int(client)
    print(f"[CONNECTED] Receiver Interface for Station {client + 1} connected to SHARED CHANNEL at {IP}:{PORT}")

    while True:
        data = receive_message(receiver)
        if not data:
            print("Channel Destroyed")
            break
        print("Data Received : " + data + "\n")

if __name__ == "__main__":
    main()