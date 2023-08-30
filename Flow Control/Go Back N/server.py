import socket
import random

HEADERSIZE = 10
PACKET_SIZE = 8
PORT = 1234
ACK = 0
SEQ = 1
PROBABILITY = 0.3

# Create a socket
# socket.AF_INET - address family, IPv4, some otehr possible are AF_INET6, AF_BLUETOOTH, AF_UNIX
# socket.SOCK_STREAM - TCP, conection-based, socket.SOCK_DGRAM - UDP, connectionless, datagrams, socket.SOCK_RAW - raw IP packets
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


server_socket.bind((socket.gethostname(), PORT))

server_socket.listen()

client_socket, addr = server_socket.accept()
print("Connection established from " + str(addr[0]))


def injectError(data) : 
    err = random.randint(0,1)
    if err:
        data = '1' + str(random.randint(0,8)) + data[2:]
    return data

def extract_frame(data):
    ind = PACKET_SIZE
    msg = ""
    if(data[ind] == '/'):
        msg = data[0:ind]
        ind = ind + 1
    else:
        msg = data[0:ind].rstrip()
        msg = msg[:-1]
    return {
            'pkt_type' : int(data[ind]),

            'packet_no' : int(data[ind+1:]),
            
            'res' : msg, 
            }

def createFrame(pkt_type, seq_no, msg):
    msg = msg + "/"
    msg = msg = f"{msg:<{PACKET_SIZE}}"
    message = msg + str(pkt_type) + str(seq_no)
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

recv = {}
ack_to_Sent = 0

# frame[i] = packet, packet = length + "--"(header) + "data --"(pkt_size)+type+seq_no
while True:
    
    client_response = receive_message(client_socket)
    if client_response is False:
        break
    
    client_response = extract_frame(client_response)

    packet_recv_no = client_response['packet_no']
    
    if client_response['pkt_type'] == SEQ  and  packet_recv_no == ack_to_Sent : 
        recv[packet_recv_no] = client_response['res']
        print("Packet "+ str(ack_to_Sent) + " Received")
        prob = random.uniform(0, 1)
        if prob > PROBABILITY:
            client_socket.send(createFrame(ACK,ack_to_Sent,"ACK").encode('utf-8'))
            print("ACK sent for : " + str(ack_to_Sent) + "\n")
            ack_to_Sent = ack_to_Sent + 1
        else:
            print("ACK for Packet " + str(ack_to_Sent) + " Lost!!\n")
    else:
        print("Invalid Packet Seq No - "+ str(packet_recv_no))
        print("Packet Discarded due not in order\n")

recv_data = ""
for frame in sorted(list(recv.keys())):
    recv_data += recv[frame]

print("Received data : " + recv_data)
server_socket.close()


