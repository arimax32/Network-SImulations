import socket
import threading
import os

IP = socket.gethostbyname(socket.gethostname())
PORT = 4449
ADDR = (IP, PORT)
FORMAT = "utf-8"
HEADERSIZE = 10
clients = []
root = []
IP = {}
dnsTree = {}

def LoadTree():
    nodes = os.listdir("Domain-Tree")
    for node in nodes:
        file = open("Domain-Tree\\" + node,"r")
        childs = file.readlines()
        file.close()
        for i,child in enumerate(childs):
            child = child.strip().split(",")
            if i == 0:
                if int(child[0]) == 1:
                    root.append(node[:-4])
            else:
                try:
                    dnsTree[node[:-4]].append(child[0])
                except:
                    dnsTree[node[:-4]] = [child[0]]
                if len(child) > 1:
                    IP[child[0]] = ' , '.join(child[1:])

def createSubTree(domain,node,leaf,ip,level):
    while leaf < node:
        f = open("Domain-Tree\\" + domain[node] + ".txt","w")
        f.write(f"{level}\n{domain[node-1]}")
        dnsTree[domain[node]] = [domain[node-1]]
        if node == leaf + 1:
            f.write(f",{ip}")
        node -= 1
        level += 1
        f.close()

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

def updateTable(server,lock):
    while True : 
        data = input("")
        if data == "exit":
            for client in clients:
                client.close()
            server.close()
            break
        lock.acquire()
        #domain_name - Ip
        ind = data.index("-")
        domain = data[0:ind].strip()
        ip = data[ind+1:].strip()
        domain = domain.split(".")
        leaf = 0
        if domain[0] == "www":
            leaf = 1
        node = len(domain) - 1
        found = True
        level = 1
        if domain[node] in root:
            par = domain[node]
            node -= 1
            level += 1
            while leaf <= node: 
                if domain[node] in dnsTree[par]:
                    par = domain[node]
                    node -= 1
                else:
                    found = False
                    file = open("Domain-Tree\\" + par + ".txt","a")
                    dnsTree[par].append(domain[node])
                    file.write(f"\n{domain[node]}")
                    if leaf == node:
                        file.write(f",{ip}")
                    file.close()
                    createSubTree(domain,node,leaf,ip,level)
                    break
                level += 1
        else:
            found = False
            root.append(domain[node])
            createSubTree(domain,node,leaf,ip,level)
        if found:
            if ip in IP[domain[leaf]]:
                print("Entry already exist's  in DNS TABLE\n")
            else:
                IP[domain[leaf]] += ',' + ip
                print("DNS TABLE UPDATED\n")
        else:
            IP[domain[leaf]] = ip
            print("DNS TABLE UPDATED\n")
        lock.release()

def handle_client(client,n):
    while True:
        domain = receive_message(client)
        if not domain : 
            index = clients.index(client)
            clients.remove(client)
            client.close()
            print(f"\nClient {n} Disconnected")
            break

        msg = ""
        domain = domain.split(".")
        leaf = 0
        if domain[0] == "www":
            leaf = 1
        node = len(domain) - 1
        if domain[node] in root:
            par = domain[node]
            node -= 1
            while leaf <= node:
                if domain[node] in dnsTree[par]:
                    if leaf == node:
                        msg = IP[domain[node]]
                    par = domain[node]
                    node -= 1
                else:
                    msg = "Domain doesn't exist in DNS Table"
                    break
        else:
            msg = "Domain doesn't exist in DNS Table"
        client.send(createFrame(msg).encode(FORMAT))

def main():
    LoadTree()
    print("DNS TREE LOADED\n")
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(ADDR)
    server.listen()
    num = 0
    lock = threading.Lock()
    thread = threading.Thread(target=updateTable,args=(server,lock,))
    thread.start()
    while True:
        client, address = server.accept()
        clients.append(client)
        num += 1
        print(f"Client {num} Connected , {address}")
        thread = threading.Thread(target=handle_client, args=(client,num))
        thread.start()



if __name__ == "__main__":
    main()














