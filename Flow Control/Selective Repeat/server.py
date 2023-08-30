import socket
import random

HEADERSIZE = 10
PACKET_SIZE = 8
WINDOW_SIZE = 4
PORT = 1234
ACK = 0
SEQ = 1
NAK = 2
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

def Corrupted(frame):
    return False

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

total_packets = int(receive_message(client_socket))

recv = dict()
last_seen, Rn, end_window = -1,0,min(total_packets,WINDOW_SIZE)
marked = []
for i in range(total_packets+1):
    marked.append(False)

NakSent = False
# frame[i] = packet, packet = length + "--"(header) + "data --"(pkt_size)+type+seq_no
while True:
    
    client_response = receive_message(client_socket)
    if client_response is False:
        break
    
    client_response = extract_frame(client_response)

    packet_recv_no = client_response['packet_no']
    
    if Corrupted(client_response):
        if not NakSent:
            # send Nack for Rn 
            NakSent = True
            print("NACK Sent for packet : " + str(Rn))
            client_socket.send(createFrame(NAK,Rn,"NAK").encode('utf-8'))
        continue

    if client_response['pkt_type'] == SEQ :
        last_seen = max(last_seen,packet_recv_no)
        marked[packet_recv_no] = True
        if packet_recv_no == Rn: 
            recv[packet_recv_no] = client_response['res']
            print("Packet "+ str(Rn) + " Received")
            if last_seen == Rn :
                #Received in order
                client_socket.send(createFrame(ACK,Rn,"ACK").encode('utf-8'))
                print("ACK sent for : " + str(Rn) + "\n")
                Rn = Rn + 1
                # prob = random.uniform(0, 1)
                # if prob > PROBABILITY:
                #     client_socket.send(createFrame(ACK,Rn,"ACK").encode('utf-8'))
                #     print("ACK sent for : " + str(Rn) + "\n")
                #     Rn = Rn + 1
                # else:
                #     print("ACK for Packet " + str(Rn) + " Lost!!\n")
            else:
                NakSent = False
                nak_packet = end_window
                for pkt in range(Rn,end_window):
                    if not marked[pkt]:
                        nak_packet = pkt
                        break
                Rn = nak_packet
                if nak_packet == end_window:
                    #Send Ack for current window and shift to new window
                    client_socket.send(createFrame(ACK,end_window-1,"ACK").encode('utf-8'))
                    print("ACK Sent for Packet " + str(end_window-1) + "\nCurrent Window Received\n")
                else:
                    #Send NAK 
                    NakSent = True
                    client_socket.send(createFrame(NAK,nak_packet,"NACK").encode('utf-8'))
                    print("NAK Sent for Packet " + str(nak_packet) + "\n")\
        
        else:
            #Received out of order
            recv[packet_recv_no] = client_response['res']
            print("Received Packet : " + str(packet_recv_no) +  " Out of Order")
            if not NakSent : 
                end_window = min(total_packets,Rn + WINDOW_SIZE)
                NakSent = True
                client_socket.send(createFrame(NAK,Rn,"NAK").encode('utf-8'))
                print("NAK Sent for Packet " + str(Rn) + "\n")\

    else:
        print("Invalid Packet Seq No - "+ str(packet_recv_no))
        print("Packet Discarded due not in order\n")


recv_data = ""
sequence = sorted(list(recv.keys()))
for seq_no in sequence:
    recv_data += recv[seq_no]

print("Received data : " + recv_data)
server_socket.close()


