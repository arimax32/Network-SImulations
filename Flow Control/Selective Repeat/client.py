import socket
import random
import time

PORT = 1234
HEADERSIZE = 10
PACKET_SIZE = 8
TIMER = 5
WINDOW_SIZE = 4
PACKET_SIZE = 8
ACK = 0
SEQ = 1
NAK = 2
PROBABILITY = 0.6


sender = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
sender.connect((socket.gethostname(),PORT))

def injectError(data) : 
    err = random.randint(0,1)
    if err:
        data = '0' + str(random.randint(0,8)) + data[2:]
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

def createDataPackets(data) : 
	data_frames = []
	l = len(data)
	pkt_no,i = 0,0
	while i < l:
		data_frames.append(createFrame(SEQ,pkt_no,data[i:min(i+PACKET_SIZE,l)]).encode('utf-8'))
		pkt_no = pkt_no + 1
		i = i + PACKET_SIZE
	print("Total Packets = " + str(pkt_no)+"\n")
	return data_frames,pkt_no

def receive_message(client_socket):
    client_socket.settimeout(TIMER)
    try:
        msg_header = client_socket.recv(HEADERSIZE)

        if not len(msg_header):
            return False

        msg_len = int(msg_header.decode('utf-8').strip())

        data = client_socket.recv(msg_len).decode('utf-8')
        client_socket.settimeout(None)
        return data,False

    except:
    	client_socket.settimeout(None)
    	return False,True

data = input("Enter the data to be sent : ")
frames,last_packet = createDataPackets(data)
WINDOW_SIZE = min(WINDOW_SIZE,last_packet)
base_pkt,last_sent = 0,0
nack_pkt_sent = -1
nack_recv = False

#send length
len_msg = str(last_packet)
len_msg = f"{len(len_msg):<{HEADERSIZE}}" + len_msg
sender.send(len_msg.encode('utf-8'))

while True:

	while last_sent - base_pkt < WINDOW_SIZE  and  last_sent < last_packet : 
		prob = random.uniform(0,1)
		if prob > PROBABILITY:
			sender.send(frames[last_sent])
			print("Packet "+ str(last_sent) + " Sent\n")
		else:
			print("Packet "+ str(last_sent) + " Lost!!\n")
		last_sent = last_sent + 1

	receiver_res,TIMEOUT = receive_message(sender)

	if TIMEOUT:
		send_pkt = base_pkt
		if nack_recv:
			send_pkt = nack_pkt_sent
		print("Timeout Occured\nResending packet " + str(send_pkt) + "\n")
		print("Packet "+ str(send_pkt) + " Sent")
		sender.send(frames[send_pkt])
		print()
	else:
		receiver_res = extract_frame(receiver_res)
		packet_no = receiver_res['packet_no']
		if receiver_res['pkt_type'] == ACK:
			print("Received ACK for Packet : " + str(packet_no))
			if packet_no - base_pkt + 1 == WINDOW_SIZE:
				print("Entire Window ["+str(base_pkt)+","+str(packet_no)+"] Received\n")
			else :
				print()
			base_pkt = packet_no + 1
			nack_recv = False

		elif receiver_res['pkt_type'] == NAK:
			if packet_no >= base_pkt and packet_no < last_packet:
				print("NACK  Received for Packet " + str(packet_no) + "\n")
				print("Resending packet " + str(packet_no) + "\n")
				print("Packet "+ str(packet_no) + " Sent")
				sender.send(frames[packet_no])
				nack_pkt_sent = packet_no
				nack_recv = True
				print()
			else :
				print("Invalid NACK Received\n")


	if base_pkt  == last_packet : 
		break

print("\nAll Packets sent")
sender.close()

	
