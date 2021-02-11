#!/usr/bin/python3

# powerssha:T0Y9rpmtjVSLIuEBn71b@networks-teaching-ftp.ccs.neu.edu

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
		# parse url import for user/pass/host/port/path
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
	URL = ""
	if param1URL:
		URL = param1URL
	else:
		URL = param2URL

	username = URL[0]
	password = URL[1]
	hostname = URL[2]
	port = URL[3]
	path = URL[4]

	def createSocket():
		"creates a socket"
		try:
			return socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		except socket.error:
			print('Error: Failed to create socket')
			sys.exit(1)
	
	def connectSocket(sock, ip, port):
		"connects a given socket to the given ip and port"
		try:
			remote_ip = socket.gethostbyname( ip )
		except socket.gaierror:
			print('Error: Hostname could not be resolved. Exiting')
			sys.exit(1)
		try:
			sock.connect((remote_ip, port))	
		except:
			print('Error Connecting to Host: ' + ip + ' on port ' + str(port))
			sys.exit(1)

	def recieveMessage( sock ):
		"This recieves a message from the socket argument"
		total_data = []
		data = b''
		while True:
			data = sock.recv(1024)
			if not data:
				break
			if b'\r\n' in data:
				total_data.append(data[:data.find(b'\r\n')])
				break
			total_data.append(data)
			if len(total_data) > 1:
				last_pair = total_data[-2] + total_data[-1]
				if b'\r\n' in last_pair:
					total_data[-2] = last_pair[:last_pair.find(b'\r\n')]
					total_data.pop()
					break
		return b''.join(total_data).decode()

	def sendMessage( sock, message ):
		"This sends a message to the socket argument"
		try:
			sock.sendall(message.encode())
		except socket.error:
			print('Send failed')
			sys.exit(1)
		time.sleep(.2)
		response = recieveMessage(sock)
		print(response)
		return response

	def signIntoFTP(sock):
		"signes into the FTP with given creds"
		sendMessage(sock, "USER " + username + "\r\n")
		if password != "":
			sendMessage(sock, "PASS " + password + "\r\n")

	def initializeFTP(sock):
		"initializes the FTP to send or recieve data"
		sendMessage(sock, "TYPE I\r\n")
		sendMessage(sock, "MODE S\r\n")
		sendMessage(sock, "STRU F\r\n")

	# def uploadFile( path ):
	# 	initializeFTP()
	# 	sendMessage(sock, "PASV\r\n")
	# 	sendMessage(sock, "STOR " + path + "\r\n")

	# def downloadFile( path ):
	# 	initializeFTP()
	# 	sendMessage(sock, "RETR " + path + "\r\n")

	def openDataSocket(sock):
		"opens/returns a data socket from PASV command"
		data = sendMessage(sock, "PASV\r\n")
		startParen = data.find("(")
		endParen = data.find(")")
		ipAndPort = data[startParen+1:endParen].split(",")
		dataIP = ".".join(ipAndPort[:4])
		dataPort = (int(ipAndPort[4]) << 8) + int(ipAndPort[5])
		dataSocket = createSocket()
		connectSocket(dataSocket, dataIP, dataPort)
		return dataSocket

	def closeConnection(sock):
		"closes the connection on socket argument"
		sendMessage(sock, "QUIT\r\n")

	sock = createSocket()
	connectSocket(sock, hostname, port)

	signIntoFTP(sock)

	# switch logic based on operation recieved
	if operation.lower() == "mkdir":
		if param1URL:
			sendMessage(sock, "MKD " + path + "\r\n")
		else: 
			print("invalid params for mkdir")
			exit(1)
	elif operation.lower() == "rmdir":
		if param1URL:
			sendMessage(sock, "RMD " + path + "\r\n")
		else: 
			print("invalid params for rmdir")
			exit(1)
	elif operation.lower() == "rm":
		if param1URL:
			sendMessage(sock, "DELE " + path + "\r\n")
		else: 
			print("invalid params for rm")
			exit(1)
	elif operation.lower() == "ls":
		if param1URL:
			initializeFTP(sock)
			dataSocket = openDataSocket(sock)
			sendMessage(sock, "LIST " + path + "\r\n")
			while True:
				time.sleep(.2)
				try:
					recieved = recieveMessage(dataSocket)
					if not recieved:
						break
					print(recieved)
				except:
					break
		else: 
			print("invalid params for ls")
			exit(1)
	elif operation.lower() == "cp":
		print("copying")
	elif operation.lower() == "mv":
		print("moving")
	else:
		print("Error: Operation not recognized")
		exit(1)

	closeConnection(sock)
	sock.close()
	exit(0)

if __name__ == '__main__':
	main(sys.argv[1:])
