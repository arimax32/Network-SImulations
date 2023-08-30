import socket
import threading
import time
import random

IP = socket.gethostbyname(socket.gethostname())
PORT = 4456
ADDR = (IP, PORT)
SIZE = 1024
FORMAT = "utf-8"
DIST = 5
HEADERSIZE = 10
dist = [False for _ in range(31)]

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

def Isbusy(i):
    global dist
    return dist[i]

def block(i):
    global dist
    dist[i] = True

def unblock(i):
    global dist
    dist[i] = False

def unpack(data):
    return {
        'dst' : int(data[0]),
        'res' : data[1:-1],
        'status' : data[-1]
    }

def handle_client(conn, addr,n,client,lock):
    print(f"[NEW CONNECTION] {addr}  Station {client + 1}")
    conn.send(createFrame(str(n)+"$"+str(client)).encode(FORMAT))
    # station_r[client].send(createFrame(str(client)).encode(FORMAT))
    time.sleep(2)
    print("Ready for Communication")

    line_end = (n-1)*DIST
    while True:
        flag = False
        cur = (client-1)*DIST 
        dst = -1
        
        res = receive_message(conn)
        if not res:
            break

        lock.acquire()   
        packet = unpack(res) 
        if Isbusy(cur):
            print("Channel is Busy\n")
            conn.send(createFrame("0").encode(FORMAT))
        else :
            if packet['status'] == "1":    
                block(cur)
                dst = (packet['dst']-1)*DIST
                flag = True
            conn.send(createFrame("1").encode(FORMAT))
        lock.release()


        if flag:
            left,right = True,True
            i,j = cur,cur

            while left or right:
                lock.acquire()
                if left:
                    if not Isbusy(i):
                        print(f"Collision Occured at Unit {i+1}")
                        print(f"Signal from Station - {client + 1}\n")
                        left = False
                    else:
                        unblock(i)
                    if left:
                        i -= 1
                        if i >= 0:
                            if Isbusy(i) :
                                print(f"Collision Occured at Unit {i+1}")
                                print(f"Signal from Station - {client + 1}\n")
                                left = False
                                unblock(i)
                            else:
                                block(i)
                                if i == dst:
                                    # station_r[packet['dst']].send(createFrame(packet['res']).encode(FORMAT))
                                    print(f"Data received by Station {packet['dst']+1} : {packet['res']}")
                        else:
                            left = False

                if j == i:
                    right = False
                if right:
                    if (j != i+1) and (not Isbusy(j)):
                        print(f"Collision Occured at Unit {j+1}")
                        print(f"Signal from Station - {client + 1}\n")
                        right = False
                    else:
                        unblock(j)
                    if right:
                        j += 1
                        if j <= line_end : 
                            if Isbusy(j) :
                                print(f"Collision Occured at Unit {j+1}")
                                print(f"Signal from Station - {client + 1}\n")
                                right = False
                                unblock(j)
                            else:
                                block(j)
                                if j == dst:
                                    # station_r[packet['dst']].send(createFrame(packet['res']).encode(FORMAT))
                                    print(f"Data received by Station {packet['dst']+1} : {packet['res']}")
                        else:
                            right = False
                lock.release()
                time.sleep(2)

    print(f"[DISCONNECTED] {addr} Station - {client + 1}")
    conn.close()

def main():
    N = int(input("Enter the number of Stations : "))
    print("[STARTING] SHARED CHANNEL is starting")
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(ADDR)
    server.listen()
    print(f"[LISTENING] Server is listening on {IP}:{PORT}.")

    lock = threading.Lock()
    for i in range(N):
        conn_c, addr_c = server.accept()
        # conn_r, addr_r = server.accept()
        # station_c[i] = conn_c
        # station_r[i] = conn_r
        thread = threading.Thread(target=handle_client, args=(conn_c, addr_c,N,i,lock))
        thread.start()

if __name__ == "__main__":
    main()