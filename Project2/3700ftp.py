#!/usr/bin/python3

# # set up variables and socket
	# # username = "powerssha"
	# # password = "T0Y9rpmtjVSLIuEBn71b"
	# #port = 21
	# #hostname = "networks-teaching-ftp.ccs.neu.edu"

# Import necessary libraries
import socket
import sys
import time

def main(argv):
	operation = ""
	param1 = ""
	param2 = ""
	
	if len(argv) > 3:
		print('Error: Bad input')
		sys.exit(1)
	if len(argv) > 2:
		param2 = argv[2]
	if len(argv) > 1:
		param1 = argv[1]
	if len(argv) > 0:
		operation = argv[0]

	def parseURL( url ):
		output = ["anonymous", "", "", 21, ""]
		header = url[:6]
		if header == "ftp://":
			# is a url
			payload = url[6:]
			payload = payload.split("/")
			if len(payload) > 1:
				output[4] = ("/").join(payload[1:])
				payload = payload[0]
				payload = payload.split("@")
				if len(payload) == 2:
					# user and host
					userPass = payload[0].split(":")
					if len(userPass) > 2:
						print("bad formed url")
						return []
					else:
						if len(userPass) > 1:
							output[1] = userPass[1]
						output[0] = userPass[0]
					hostPort = payload[1].split(":")
					if len(hostPort) > 2:
						print("bad formed url")
						return []
					else:
						if len(hostPort) > 1:
							output[3] = int(hostPort[1])
						output[2] = hostPort[0]
				elif len(payload) == 1:
					# only host and port
					hostPort = payload[0].split(":")
					if len(hostPort) > 2:
						print("bad formed url")
						return []
					else:
						if len(hostPort) > 1:
							output[3] = int(hostPort[1])
						output[2] = hostPort[0]
				else:
					print("bad formed url")
					return []
			else:
				print("bad formed url")
				return []
			return output
		else:
			return []

	
	param1URL = parseURL(param1)
	param2URL = parseURL(param2)
	
	if param1URL and param2URL:
		print("Error: Recieved two FTP params")
		exit(1)
	if not param1URL and not param2URL:
		print("Error: Did not recieve an FTP param")
		exit(1)

	if param1URL:
		username = param1URL[0]
		password = param1URL[1]
		hostname = param1URL[2]
		port = param1URL[3]
		path = param1URL[4]
	else:
		username = param2URL[0]
		password = param2URL[1]
		hostname = param2URL[2]
		port = param2URL[3]
		path = param2URL[4]

	# create socket
	try:
		sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	except socket.error:
		print('Error: Failed to create socket')
		sys.exit(1)
	try:
		remote_ip = socket.gethostbyname( hostname )
	except socket.gaierror:
		print('Error: Hostname could not be resolved. Exiting')
		sys.exit(1)


	# method to send a message to the server
	def sendMessage( message ):
		"This sends a message to the server"
		try:
			sock.sendall(message.encode())
		except socket.error:
			print('Send failed')
			sys.exit(1)
		return getResponse()

	# method to recieve a message from the server
	def recieveMessage():
		"This recieves a message from the server"
		total_data = []
		data = b''
		while True:
			data = sock.recv(8192)
			if b'\n' in data:
				total_data.append(data[:data.find(b'\n')])
				break
			total_data.append(data)
			if len(total_data) > 1:
				last_pair = total_data[-2] + total_data[-1]
				if b'\n' in last_pair:
					total_data[-2] = last_pair[:last_pair.find(b'\n')]
					total_data.pop()
					break
		return b''.join(total_data).decode()

	def getResponse():
		response = recieveMessage()
		responseCode = int(response.split()[0])
		if responseCode >= 100 and responseCode < 200:
			print(response)
		elif responseCode >= 200 and responseCode < 300:
			print(response)
		elif responseCode >= 300 and responseCode < 400:
			print(response)
		else:
			print(response)
			exit(1)

	# Connect to remote server
	try:
		sock.connect((remote_ip, port))	
	except:
		print('Error Connecting to Host: ' + remote_ip + ' on port ' + str(port))
		sys.exit(1)

	def initializeFTP():
		sendMessage("USER " + username + "\r\n")
		if password != "":
			sendMessage("PASS " + password + "\r\n")
		sendMessage("TYPE I\r\n")
		sendMessage("MODE S\r\n")
		sendMessage("STRU F\r\n")

	def uploadFile( path ):
		sendMessage("STOR " + path + "\r\n")

	def downloadFile( path ):
		sendMessage("RETR " + path + "\r\n")

	def openDataChannel():
		sendMessage("PASV\r\n")

	def closeConnection():
		sendMessage("QUIT\r\n")

	initializeFTP()

	if operation.lower() == "ls":
		if param1URL:
			sendMessage("LIST " + path + "\r\n")
		else: 
			print("invalid params for ls")
			exit(1)
	elif operation.lower() == "mkdir":
		if param1URL:
			sendMessage("MKD " + path + "\r\n")
		else: 
			print("invalid params for mkdir")
			exit(1)
	elif operation.lower() == "rm":
		if param1URL:
			sendMessage("DELE " + path + "\r\n")
		else: 
			print("invalid params for rm")
			exit(1)
	elif operation.lower() == "rmdir":
		if param1URL:
			sendMessage("RMD " + path + "\r\n")
		else: 
			print("invalid params for rmdir")
			exit(1)
	elif operation.lower() == "cp":
		print("copying")
	elif operation.lower() == "mv":
		print("moving")
	else:
		print("Error: Operation not recognized")
		exit(1)

	sock.close()
	exit(0)

if __name__ == '__main__':
	main(sys.argv[1:])
