import socket
import random
import time

PORT = 1234
PROBABILITY = 0.3
HEADERSIZE = 10
PACKET_SIZE = 8
TIMER = 5
ACK = 0
SEQ = 1

sender = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
sender.connect((socket.gethostname(),PORT))

def injectError(data) : 
	prob = random.uniform(0,1)
	print(prob)
	if prob < PROBABILITY:
		data = '0' + str(random.randint(0,8)) + data[2:]
	return data

def extract_frame(data):
   return {'pkt_type' : int(data[0]),'frame_id' : int(data[1]),'res' : data[2:]}


def createFrame(pkt_type, seq_no, msg):
    message = str(pkt_type) + str(seq_no) + msg
    # message = injectError(message)
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
frame_no = 0
ack_recv = True

while True:

	if ack_recv:
		sender.send(frames[frame_no])
		print("Frame "+ str(frame_no) + " sent\n")


	receiver_res,TIMEOUT = receive_message(sender)


	if TIMEOUT:
		print("Timeout Occured")
		print("Resending Frame " + str(frame_no) + "\n")
		ack_recv = True
		continue
	

	if receiver_res is False:
		break
	
	receiver_res = extract_frame(receiver_res)
	

	if receiver_res['pkt_type'] == ACK and receiver_res['frame_id'] == frame_no : 
		print("ACK Received\nReady to send Frame : " + str(frame_no+1)+"\n")
		ack_recv = True
		frame_no = frame_no + 1
	else:
		ack_recv = False
		print("Invalid ACK Received\n")

	if frame_no == last_packet:
		break


print("All Packets sent")
sender.close()

	
