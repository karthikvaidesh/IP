#!/usr/bin/python        
from _thread import *
import pickle as p  
import socket as s  
import platform as pf            
import time as t					
			
#Creating a socketd binding it to self's ip address and port 7734
soc = s.socket()     
host = s.gethostname()
port = 7734
soc.bind((host, port))
print("NOW ACTIVE")
soc.listen()
active_peer_list = []
rfc_list = [] 
merged_list = []

#Create a new thread for each client request
def create_thread(conn, addr):
    global active_peer_list, rfc_list, merged_list
    conn.send(bytes('Connected to server ' + host, 'utf-8'))

    #Populating the global lists for RFCs and Peers
    print(p.loads(conn.recv(8192)))
    data = p.loads(conn.recv(8192))
    upload_port = data[0]
    peer_keys = ['Hostname', 'Port Number']
    value = [addr[0], str(upload_port)]
    active_peer_list.insert(0, dict(zip(peer_keys, value)))
    rfc_keys = ['RFC Number', 'RFC Title', 'Hostname']
    for rfc in data[1]:
        rfc_number = rfc['RFC Number']
        rfc_title = rfc['RFC Title']
        value = [str(rfc_number), rfc_title, addr[0]]
        rfc_list.insert(0, dict(zip(rfc_keys, value)))
    merged_keys = ['RFC Number','RFC Title','Hostname','Port Number']
    for rfc in data[1]:
        rfc_number = rfc['RFC Number']
        rfc_title = rfc['RFC Title']
        value = [str(rfc_number), rfc_title, addr[0], str(data[0])]
        merged_list.insert(0, dict(zip(merged_keys, value)))
    while True:
        # try:
        print_data = conn.recv(4096)
        data = p.loads(print_data)
        #print(print_data)
        if type(data) == str:
            print(data)
        else: print(data[0])
        #print(print_data.decode('utf-8'), end="")
        if data == "EXIT":
            break
        if type(data) == str:
            conn.send(bytes("P2P-CI/1.0 200 OK", 'utf-8'))
            #print("KARTHIK " + str(new_data))
            conn.send(p.dumps((merged_list, ['RFC Number', 'RFC Title', 'Hostname', 'Port Number'])))
        else:
            if data[0][0] == "A":
                conn.send(bytes("P2P-CI/1.0 200 OK \nRFC "+ data[1] +" "+data[4]+" "+str(addr[0])+" "+str(data[3]), 'utf-8'))
                keys = ['RFC Number', 'RFC Title', 'Hostname']
                value = [str(data[1]), data[4], addr[0]]
                rfc_list.insert(0, dict(zip(keys, value)))
                keys = ['RFC Number', 'RFC Title', 'Hostname', 'Port Number']
                value = [str(data[1]), data[4], addr[0], str(upload_port)]
                merged_list.insert(0, dict(zip(keys, value)))
                '''print("KARTHIK 2\n")
                for value in rfc_list:
                    print(' '.join([value[key] for key in rfc_keys]))'''

            if data[2] == "0": #for GET
                for d in merged_list:
                    if d['RFC Number'] == data[1]:
                        response = d
                        break
                    else:
                        response = False
                if not response:
                    msg= "P2P-CI/1.0 404 Not Found"+"\n"\
                            "Date: " + t.strftime("%a, %d %b %Y %X %Z", t.localtime()) + "\n"\
			     	"OS: "+str(pf.platform())+"\n"
                else:
                    msg	= "P2P-CI/1.0 200 OK"+"\n"
                new_data = p.dumps((response,msg))
                conn.send(new_data)

            elif data[2] == "1": #for LOOKUP
                response = []
                for d in merged_list:
                    if d['RFC Number'] == data[1]:
                        response.append(d)
                if len(response) == 0:
                    msg= "P2P-CI/1.0 404 Not Found "+"\n"\
                            "Date: "+ t.strftime("%a, %d %b %Y %X %Z", t.localtime()) + "\n"\
                            "OS: "+str(pf.platform())+"\n"
                else:
                    msg= "P2P-CI/1.0 200 OK "+"\n"
                #print("KARTHIK 3\n")
                #print(response)
                #print(msg)
                new_data = p.dumps((response,msg))
                conn.send(new_data)
        # except Exception:
        #     active_peer_list[:] = [d for d in active_peer_list if d.get('Hostname') != addr[0]]   #Removing Client's information from server data structures when the client leaves the system
        #     rfc_list[:] = [d for d in rfc_list if d.get('Hostname') != addr[0]]
        #     merged_list[:] = [d for d in merged_list if d.get('Hostname') != addr[0]]
        #     conn.close()


    active_peer_list[:] = [d for d in active_peer_list if d.get('Hostname') != addr[0]]   #Removing Client's information from server data structures when the client leaves the system
    rfc_list[:] = [d for d in rfc_list if d.get('Hostname') != addr[0]]
    merged_list[:] = [d for d in merged_list if d.get('Hostname') != addr[0]]
    conn.close()


while True:
    conn, addr = soc.accept()
    start_new_thread(create_thread, (conn, addr))
soc.close()
