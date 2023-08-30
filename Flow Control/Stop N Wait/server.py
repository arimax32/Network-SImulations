import socket
import random

HEADERSIZE = 10
PROBABILITY = 0.3
ACK = 0
SEQ = 1
PORT = 1234

# Create a socket
# socket.AF_INET - address family, IPv4, some otehr possible are AF_INET6, AF_BLUETOOTH, AF_UNIX
# socket.SOCK_STREAM - TCP, conection-based, socket.SOCK_DGRAM - UDP, connectionless, datagrams, socket.SOCK_RAW - raw IP packets
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


server_socket.bind((socket.gethostname(), PORT))

server_socket.listen(5)

client_socket, addr = server_socket.accept()
print("Connection established from " + str(addr))


def injectError(data) :
    prob = random.uniform(0,1)
    if prob < PROBABILITY:
        data = '1' + str(random.randint(0,8)) + data[2:]
    return data

def extract_frame(data):
    return {'pkt_type' : int(data[0]),'frame_id' : int(data[1]),'res' : data[2:]}

def createFrame(pkt_type, seq_no, msg):
    message = str(pkt_type) + str(seq_no) + msg
    #message = injectError(message)
    return f"{len(message):<{HEADERSIZE}}" + message


def receive_message(client_socket):
    try:
        msg_header = client_socket.recv(HEADERSIZE)
        if not len(msg_header):
            return False

        msg_len = int(msg_header.decode('utf-8').strip())
        data = client_socket.recv(msg_len).decode('utf-8')
        return data

    except:
        return False

frame_no = 0
recv = []

while True:
    
    client_response = receive_message(client_socket)
    if client_response is False:
        break
    
    client_response = extract_frame(client_response)
    

    if client_response['pkt_type'] == SEQ and client_response['frame_id'] == frame_no:
        recv.append(client_response['res'])
        prob = random.uniform(0,1)
        if prob > PROBABILITY:
            print("Packet " + str(frame_no) + " Received")
            print("ACK Sent\n")
            client_socket.send(createFrame(ACK,frame_no,"ACK").encode('utf-8'))
            frame_no = frame_no + 1
        else:
            recv.pop()
            print("ACK for Packet "+str(frame_no) + " Lost!!\n")
    else : 
        print("Invalid Packet")
        print("Frame " + str(frame_no) + " not Received\n")

recv_data = ""
for d in recv:
    recv_data = recv_data + d
print("Data Received : " + recv_data)
server_socket.close()


