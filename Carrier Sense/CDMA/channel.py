import copy
import time

code = {'0' : -1 , '1' : 1}
dcode = {1 : 1, -1 : 0}

def generateWalshTable(n):
    print('Generating Walsh table ...')
    p = 1
    prevtable = [ [1] ]
    while p < n:
        p *= 2
        curtable = []
        for i in range(p):
            tup = []
            for j in range(p):
                tup.append(0)
            curtable.append(tup)
        for i in range(0,p//2):
            for j in range(0,p//2):
                curtable[i][j] = prevtable[i][j]
                curtable[i+p//2][j] = prevtable[i][j]
                curtable[i][j+p//2] = prevtable[i][j]
                curtable[i+p//2][j+p//2] = -1*prevtable[i][j]   
        prevtable = curtable
        
    print('Printing Walsh table :')
    for i in range(p):
        for j in range(p):
            if prevtable[i][j] == 1:
                print(end=' ')
            print(prevtable[i][j],end=' ')
        print()
    return prevtable,p

def updateWalshTable(walshtable, bit, data, p):
    n = len(data)
    table = copy.deepcopy(walshtable)
    for station in range(n):
        for j in range(p):
            if bit >= len(data[station]):
                table[station][j] = 0
            else:
                table[station][j] *= code[data[station][bit]]

    sum_t = []
    for j in range(p):
        tsum = 0
        for i in range(n):
            tsum += table[i][j]
        sum_t.append(tsum)
    return sum_t

def receive_bit(station, bit, data, wtable,sum_t,p):
    
    if bit >= len(data[station]):
        print("Received Nothing |",end=' ')
    else:
        recv = 0
        for i in range(p):
            recv += wtable[station][i]*sum_t[i]
        recv = recv//p
        print(f"Received bit for station {station} : {dcode[recv]} |", end = ' ') 

if __name__ == '__main__':
    n = int(input('Enter number of stations: '))
    data = []
    table,p = generateWalshTable(n)

    for i in range(n):
        x = input(f"Enter Data for Station {i} : ")
        data.append(x)

    l = 1
    for d in data:
        l = max(l,len(d))
    print("Data Received by Channel\n")

    for j in range(0,l):
        sum_table = updateWalshTable(table,j,data,p)
        print("Channel Status : ")
        for i in range(n):
            receive_bit(i,j,data,table,sum_table,p)
        print()
        time.sleep(2)
