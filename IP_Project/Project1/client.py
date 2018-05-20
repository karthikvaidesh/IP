#!usr/bin/python

import platform as pf
import pickle as p
import os
import random
import socket as s
import time as t
from _thread import *

upload_port = 8000 + random.randint(1, 100)
list_rfc = []
soc = s.socket()
server_ip = "10.154.47.215" #v.imp -> need to hardcode everytime as server is started on a new machine
server_port = 7734
#print("before connect")
soc.connect((server_ip, server_port))
#print("after connect")

peer_keys = ['RFC Number', 'RFC Title']
rfc_no = [num[num.find("c") + 1 : num.find(".")] for num in os.listdir(os.getcwd() + "/rfc") if 'rfc' in num]
rfc_title = [num[0 : num.find(".")] for num in os.listdir(os.getcwd() + "/rfc") if 'rfc' in num]
msg = ""
for no, title in zip(rfc_no, rfc_title):
        entry = [no, title]
        list_rfc.insert(0, dict(zip(peer_keys, entry)))
        msg += "ADD" + " RFC " + str(no)+" P2P-CI/1.0 \n"\
		"Host: " + str(s.gethostname())+" ("+ str(soc.getsockname()[0])+") \n"\
		"Port: " + str(soc.getsockname()[1])+"\n"\
		"Title: " + str(title)+"\n"

soc.send(p.dumps(msg))
soc.send(p.dumps([upload_port, list_rfc]))
#print("after connectjnhjnhj")
print(soc.recv(4096).decode('utf-8'))
soc.close

def get_input():
	try:
		ip = input("Enter 1 for ADD\n2 for LIST\n3 for GET\n4 for LOOKUP\n5 to QUIT\n")

		if ip == "1":
			rfc_no = input("Enter the RFC number : ")
			rfc_title = input("Enter the RFC title : ")

			path = os.getcwd()
			filename = "rfc" + rfc_no + ".txt"
			type_of_os = pf.system()
			file_path=""
			if type_of_os == "Windows":
				file_path = path + "\\rfc\\" + filename
				
			else:
				file_path = path + "/rfc/" + filename

			if not os.path.isfile(file_path) :
				print(filename+" does not exist in your system")

			else:
				
				msg = "ADD" + " RFC " + str(rfc_no)+" P2P-CI/1.0 \n"\
				"Host: " + str(s.gethostname())+" ("+ str(soc.getsockname()[0])+") \n"\
				"Port: " + str(soc.getsockname()[1])+"\n"
				"Title: " + str(rfc_title)+"\n"
				soc.send(p.dumps([msg, rfc_no, soc.getsockname()[0], upload_port, rfc_title]))
				print(soc.recv(4096).decode('utf-8'))
			get_input()
		elif ip == "2":
			msg = "LIST ALL P2P-CI/1.0 \n"\
	              "Host: " + str(s.gethostname())+" ("+ str(soc.getsockname()[0])+") \n"\
	              "Port: " + str(soc.getsockname()[1])+"\n"
			soc.send(p.dumps(msg))

			print(soc.recv(4096).decode('utf-8'), end="")
			print("\n")
			data = p.loads(soc.recv(4096))
			for rfc in data[0]:
				print(' '.join([rfc[r] for r in data[1]]))
			get_input()
		elif ip == "3":
			rfc_no = input("Enter the RFC number : ")
			rfc_title = input("Enter the RFC title : ")

			msg = "LOOKUP" + " RFC " + str(rfc_no)+" P2P-CI/1.0 \n"\
			"Host: " + str(s.gethostname())+" ("+ str(soc.getsockname()[0])+") \n"\
			"Port: " + str(soc.getsockname()[1])+"\n"
			"Title: " + str(rfc_title)+"\n"
			soc.send(p.dumps([msg, rfc_no, "0"]))

			srvr_data = p.loads(soc.recv(4096))
			#print(srvr_data)

			if srvr_data[0]:
				new_soc = s.socket()

				new_soc.connect((srvr_data[0]["Hostname"], int(srvr_data[0]["Port Number"])))

				type_of_os = pf.platform()
				msg = "GET RFC " + str(rfc_no) + " P2P-CI/1.0 \n"\
				  "Host: " + str(s.gethostname())+" ("+ str(soc.getsockname()[0])+") \n"\
				  "OS: " + str(type_of_os) + "\n"

				new_soc.send(bytes(msg, 'utf-8'))
				response = p.loads(new_soc.recv(4096))
				for x in range(len(response)):
					print(response[x])
				#print(str(response))
				#print("\n")
				#print(response[1])

				path = os.getcwd()
				filename = "rfc" + rfc_no + ".txt"
				type_of_os = pf.system()
				if type_of_os == "Windows":
					filename = path + "\\rfc\\" + filename
				else:
					filename = path + "/rfc/" + filename

				with open(filename, 'w') as f:
					f.write(response[1])

				new_soc.close()
			else:
				print(srvr_data[1])

			get_input()
		elif ip == "4":
			rfc_no = input("Enter the RFC number : ")
			rfc_title = input("Enter the RFC title : ")

			msg = "LOOKUP" + " RFC " + str(rfc_no)+" P2P-CI/1.0 \n"\
			"Host: " + str(s.gethostname())+" ("+ str(soc.getsockname()[0])+") \n"\
			"Port: " + str(soc.getsockname()[1])+"\n"\
			"Title: " + str(rfc_title)+"\n"
			soc.send(p.dumps([msg, rfc_no, "1"]))
			srvr_data = p.loads(soc.recv(4096))
			print(srvr_data[1], end = "")
			print("\n")

			for rfc in srvr_data[0]:
				print(' '.join([rfc[r] for r in ['RFC Number', 'RFC Title', 'Hostname', 'Port Number']]))

			get_input()
		elif ip == "5":
			soc.send(p.dumps("EXIT"))
			soc.close()
		else:
			print('Incorrect Input, Enter correct option')
			get_input()
	except KeyboardInterrupt:
		print("abrupt interrupt")
		soc.send(p.dumps("EXIT"))
		soc.close()
		



def response_msg(rfc_no):
	filename = "rfc" + str(rfc_no) + ".txt"
	filename = "".join(filename.split())

	if pf.system == "Windows":
		filename = "rfc\\" + filename
	else:
		filename = "rfc/" + filename

	if not os.path.exists(filename) == 0:
		file = open(filename)
		return ["P2P-CI/1.0 200 OK\n"\
                  "Date: " + t.strftime("%a, %d %b %Y %X %Z", t.localtime()) + "\n"\
                  "OS: " + str(pf.system()) + "\n"\
                  "Last-Modified: " + t.ctime(os.path.getmtime(filename)) + "\n"\
                  "Content-Length: " + str(os.path.getsize(filename)) + "\n"\
                  "Content-Type: text/text \n", str(file.read())]
	else:
		return "P2P-CI/1.0 404 Not Found\n"\
		            "Date:" + t.strftime("%a, %d %b %Y %X %Z", t.localtime()) + "\n"\
		            "OS: "+str(pf.system())+"\n"

def peer_to_peer_conn(str, i):
	upload_soc = s.socket()
	host = s.gethostname()
	upload_soc.bind((host, upload_port))
	upload_soc.listen(10)

	while True:
		conn, ip = upload_soc.accept()
		data = conn.recv(4096).decode('utf-8')
		rfc_no = data[data.index('C') + 1 : data.index('P') - 1]
		#print("Connected to ", ip)
		print(data)
		conn.send(p.dumps(response_msg(rfc_no)))
		conn.close()

start_new_thread(peer_to_peer_conn, ("hello", 1))
get_input()
