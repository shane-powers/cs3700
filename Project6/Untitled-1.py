#!/usr/bin/env python3

import sys, socket, select, time, json, random

# Your ID number
my_id = sys.argv[1]

# The ID numbers of all the other replicas
replica_ids = sys.argv[2:]

# Connect to the network. All messages to/from other replicas and clients will
# occur over this socket
sock = socket.socket(socket.AF_UNIX, socket.SOCK_SEQPACKET)
sock.connect(my_id)

def get_random_timeout():
	#Return value between 150 and 300 ms
	return random.uniform(.3, .8)

############################# PERSISTENT STATE ON ALL SERVERS
currentTerm = 0
votedFor = None
log=[{'term': 0, "action": None, "value": None, "key":None}]

############################# VOLATILE STATE ON ALL SERVERS
commitIndex = 0
lastApplied = 0

############################# VOLATILE STATE ON LEADERS
nextIndex = 0
matchIndex = 0
next_index_dict = {}

############################# OTHER IMPORTANT VARIABLES
thisRole = "follower"
numberOfMachines = len(sys.argv) - 1 # TODO THIS ISNT USED
electionTimeout = get_random_timeout() 
lastEvent = time.time() # TODO THIS ISNT USED
currentLeader = "FFFF"
STORE = {}

'''
1) leader election
	after timeout, become candidate
	increment current term
	vote for self and send request vote to all servers
	if votes from majority
		become leader, send heartbeats
	elif RPC from leader
		become follower
	elif timeout
		return to start
2) normal operation
	client sends command to leader
	leader appends command to log
	leader sends append entries to all followers
		leader retries append entries until they succeed
	once entry is committed:
		leader executes command, and returns result to client
		notifies followers of committed entries in subsequent append entries 
		followers execute committed commands in their state machines
'''

############################# SEND MESSAGE METHODS
def send_msg(msg):
	# SENDS A MESSAGE TO THE DST OF THE MESSAGE GIVEN
	sock.sendall(json.dumps(msg).encode())

def send_to_all(msg):
	# SENDS A MESSAGE TO ALL DSTs IN REPLICA_IDS
	for id in replica_ids:
		msg['dst'] = id
		sock.sendall(json.dumps(msg).encode())	


############################# REQUEST VOTE RPC METHOD
def request_vote_rpc(term, candidateId, lastLogIndex, lastLogTerm):
	global currentTerm, votedFor
	if term < currentTerm:
		msg = {'src': my_id, 'dst': candidateId, 'type': 'RequestVoteResponse', "leader": currentLeader, 'data': False}
		#print(str(my_id) + " DID NOT VOTE FOR " + str(candidateId))
		send_msg(msg)
		return
	elif votedFor == None or votedFor == candidateId:
		#grant vote
		currentTerm = term
		votedFor = candidateId
		msg = {'src': my_id, 'dst': candidateId, 'type': 'RequestVoteResponse', "leader": currentLeader, 'data': True}
		#print(str(my_id) + " VOTED FOR " + str(candidateId))
		send_msg(msg)
		return
	else:
		currentTerm = term
		msg = {'src': my_id, 'dst': candidateId, 'type': 'RequestVoteResponse', "leader": currentLeader, 'data': False}
		#print(str(my_id) + " DID NOT VOTE FOR " + str(candidateId))
		send_msg(msg)
		return

############################# APPEND ENTRIES RPC METHOD
def append_entries_rpc(term, leaderId, prevLogIndex, prevLogTerm, entries, leaderCommit):
	global log, my_id, lastEvent, currentLeader, currentTerm
	lastEvent = time.time()
	#print(str(my_id) + " RECEIVED APPEND ENTRIES FROM " + str(leaderId))
	if prevLogIndex >= len(log) or term < currentTerm or prevLogTerm != log[prevLogIndex]["term"]: 
		resp_msg = {'src':my_id,'dst':leaderId,'leader':leaderId,'type': "AppendEntriesResponse",'term': currentTerm, 'success': False, 'nextIndex': len(log)}
		send_msg(resp_msg)
	
	else:
		currentLeader = leaderId
		currentTerm = term
		if len(entries) > 0:
			 log = log[:prevLogIndex + 1]
			 for entry in entries:
				 log.append(entry)
				 if entry["key"] not in STORE:
					 STORE[entry["key"]] = entry["value"]
		resp_msg = {'src':my_id,'dst':leaderId,'leader':leaderId,'type': "AppendEntriesResponse",'term': currentTerm, 'success': True, 'nextIndex': len(log)}
		send_msg(resp_msg)
			
	
	# 	return
	# if prevLogIndex < len(log):
	# 	if log[prevLogIndex] != prevLogTerm: # TODO CATCH ERROR OUT OF BOUNDS INDEX

	# 		msg = {'src': my_id, 'dst': leaderId, 'type': 'AppendEntriesResponse', "leader": currentLeader, 'success': False}
	# 		send_msg(msg)
	# 		currentLeader = leaderId
	# 		return
	# else:
	# 	msg = {'src': my_id, 'dst': leaderId, 'type': 'AppendEntriesResponse', "leader": currentLeader, 'success': True}
	# 	send_msg(msg)
	# 	currentLeader = leaderId
	# 	return
	# 	print("!!!!!!!!!!!!!!!!!!!!!!!!!!! append entries response not sent")
	# 	# if logs are not equal
	# 	# TODO
	# if(leaderCommit > commitIndex):
	# 	commitIndex = min(leaderCommit, len(log)-1)

############################# STATE TRANSITION METHODS
receivedVotes = []

def sendHeartbeat():
	for rid in replica_ids:
		send_append_entries_for_replica(rid)

def begin_election():
	global votedFor, currentTerm, thisRole, receivedVotes
	receivedVotes = []
	#Increment current term
	currentTerm += 1
	#Change role to candidate
	thisRole = "candidate"
	#issues request vote to each of other servers
	votedFor = my_id
	data = {
		'term': currentTerm,
		'candidateId': my_id,
		'lastLogIndex': len(log) - 1,
		'lastLogTerm': log[len(log)-1]['term']
	}
	msg = {'src': my_id, 'dst': "None", 'type': 'RequestVote', "leader": currentLeader, 'data': data} # TODO MIGHT BREAK
	send_to_all(msg)
	#print(str(msg))

def make_self_leader():
	global thisRole, currentLeader, receivedVotes, currentTerm
	#print(str(my_id) + " BECAME A LEADER")
	thisRole = "leader"
	currentLeader = my_id
	receivedVotes = []
	for rid in replica_ids:
		next_index_dict[rid] = len(log)
	sendHeartbeat()

def give_up_leader(term, newLeader):
	global thisRole, currentLeader, next_index_dict
	thisRole = "follower"
	next_index_dict = {}
	currentLeader = newLeader
	currentTerm = term
	lastEvent = time.time()
	

############################# HANDLE RECEIVED MESSAGE METHODS
def handle_request_vote(msg):
	data = msg['data']
	request_vote_rpc(data['term'], data['candidateId'], data['lastLogIndex'], data['lastLogTerm'])
	
def handle_request_vote_response(msg):
	global thisRole, receivedVotes, currentTerm
	if thisRole == "candidate" and msg['dst'] == my_id:
		if msg['data'] == True:
			receivedVotes.append(msg['src'])
		if len(receivedVotes) > len(replica_ids)/2.0:
			make_self_leader() # TODO BE PREPARED TO HANDLE NOT GETTING HERE
	

def handle_append_entries(msg):
	global thisRole
	if thisRole != "follower":
		if thisRole == "leader":
			give_up_leader(msg["term"], msg["leader"])
		else:
			thisRole = "follower"
	data = msg['data']
	append_entries_rpc(data["term"], data["leaderId"], data["prevLogIndex"], data["prevLogTerm"], data["entries"], data["leaderCommit"])

def handle_append_entries_response(msg):
	global currentTerm, next_index_dict, currentLeader
	if thisRole == "leader":
		if currentTerm < msg['term']:
			give_up_leader(msg['term'], msg["leader"])
			return
		elif msg['success'] == False:
			next_index_dict[msg["src"]] = msg["nextIndex"]
		elif msg['success'] == True:
			#success true
			next_index_dict[msg["src"]] = min(len(log), msg["nextIndex"])
	else:
		currentLeader = msg["leader"]
		currentTerm = msg["term"]

def handle_redirect(msg):
	#print(str(my_id) + " is redirecting to client")
	#{"src": "<ID>", "dst": "<ID>", "leader": "<ID>", "type": "redirect", "MID": "<a unique string>"}
	msg = {'src': my_id, 'dst': msg["src"], "leader": currentLeader, 'type': 'redirect', 'MID': msg["MID"]}
	send_msg(msg)

# def echo_get(entries):
# 	global currentTerm, my_id, log, commitIndex
# 	data = {
# 		'term': currentTerm,
# 		'leaderId': my_id,
# 		'prevLogIndex': len(log) - 1,
# 		'prevLogTerm': log[len(log)-1]['term'],
# 		'entries': [entries],
# 		'leaderCommit': commitIndex
# 	}
# 	msg = {'src': my_id, 'dst': "None", 'type': 'AppendEntries', "leader": currentLeader, 'data': data}
# 	#send_to_all(msg)

def handle_get(msg):
	global commitIndex
	'''
	{"src": "<ID>", 
	"dst": "<ID>", 
	"leader": "<ID>", 
	"type": "get", 
	"MID": "<a unique string>", 
	"key": "<some key>"}
	'''
	#print(str(my_id) + " received GET request. Is leader? : " + str(currentLeader == my_id))
	if(thisRole == "leader"):
		#commitIndex += 1
		#newLogEntry = {"term": currentTerm, "action": "GET", "key":msg["key"], "value":None}
		#log.append(newLogEntry)
		#print(str(my_id) + " added " + str(newLogEntry) + "to log, and sent to everyone")
		#print(str(my_id) + " is invoking GET request")
		response = STORE[msg['key']] # will be a value or 'None'	
		#print("trying to retreive value from key: " + msg["key"])
		if response:
			#print("retreived value: " + response + ", from key: " + msg["key"])
			# {"src": "<ID>", "dst": "<ID>", "leader": "<ID>", "type": "ok", "MID": "<a unique string>", "value": "<value of the key>"}
			reply = {'src': my_id, 'dst': msg["src"], "leader": currentLeader, 'type': 'ok', "MID": msg["MID"], "value": response} 
			send_msg(reply)
		else:
			#print("retreived no value from key: " + msg["key"])
			# {"src": "<ID>", "dst": "<ID>", "leader": "<ID>", "type": "fail", "MID": "<a unique string>"}
			reply = {'src': my_id, 'dst': msg["src"], "leader": currentLeader, 'type': 'fail', "MID": msg["MID"]} 
			send_msg(reply)
	else:
		handle_redirect(msg)

# def echo_put(entries):
# 	global currentTerm, my_id, log, commitIndex
# 	data = {
# 		'term': currentTerm,
# 		'leaderId': my_id,
# 		'prevLogIndex': len(log) - 1,
# 		'prevLogTerm': log[len(log)-1]['term'],
# 		'entries': [entries],
# 		'leaderCommit': commitIndex,
# 		'leaderLog': log
# 	}
# 	msg = {'src': my_id, 'dst': "None", 'type': 'AppendEntries', "leader": currentLeader, 'data': data}
# 	send_to_all(msg)

def send_append_entries_for_replica(rid):
	global currentTerm, my_id, log, commitIndex
	#to_append = {'term': current_term, 'leaderId': leader,
	#'prevLogIndex': next_index[rid] - 1, 'prevLogTerm': log[next_index[rid] - 1]['term'], 'leaderCommit': commit_idx}
	if next_index_dict[rid] >= len(log):
		entries = []
	else:
		entries = [log[next_index_dict[rid]]]

	data = {
		'term': currentTerm,
		'leaderId': my_id,
		'prevLogIndex': next_index_dict[rid]-1,
		'prevLogTerm': log[next_index_dict[rid]-1]["term"],
		'entries': entries,
		'leaderCommit': commitIndex,
	}
	msg = {'src': my_id, 'dst': rid, 'type': 'AppendEntries', "leader": currentLeader, 'data': data}
	send_msg(msg)

def handle_put(msg):
	global commitIndex, log, currentTerm
	'''
	log=[{'term': 0, "action": None, "value": None}]
	{"src": "<ID>", 
	"dst": "<ID>", 
	"leader": "<ID>", 
	"type": "put", 
	"MID": "<a unique string>", 
	"key": "<some key>", 
	"value": "<value of the key>"}
	'''
	#print(str(my_id) + " received PUT request. Is leader? : " + str(currentLeader == my_id))
	if thisRole == "leader":
		commitIndex += 1
		newLogEntry = {"term": currentTerm, "action": "PUT", "key":msg["key"], "value":msg["value"]}
		log.append(newLogEntry)
		#print(str(my_id) + " added " + str(newLogEntry) + "to log, and sent to everyone")
		for rid in replica_ids:
			send_append_entries_for_replica(rid)
		#print(str(my_id) + " is invoking PUT request")
		STORE[msg["key"]] = msg["value"]
		#print("put key " + msg["key"] + " into store with value " + msg["value"])
		reply = {'src': my_id, 'dst': msg["src"], "leader": currentLeader, 'type': 'ok', "MID": msg["MID"]} 
		send_msg(reply)
		# TODO IN THE FUTURE ACCOUNT FOR 'TYPE FAIL'
	else:
		handle_redirect(msg)
# def handle_append_entries_response(msg):
# 	global thisRole
# 	goodResponse = {}
# 	if thisRole == "leader":
# 		goodResponse[currentTerm].append()
# 	if len(goodResponse[currentTerm]) > len(replica_ids)/2.0:
# 			print("enough good responses")
# 	else:
# 		print("not enough good responses")
		
	
############################# MAIN LOOP
while True:
	ready = select.select([sock], [], [], 0.1)[0]
	
	if sock in ready:
		msg_raw = sock.recv(32768)
		
		if len(msg_raw) == 0: continue
		msg = json.loads(msg_raw)
		
		# For now, ignore get() and put() from clients
		if msg['type'] == 'get':
			handle_get(msg)

		elif msg['type'] == 'put':
			handle_put(msg)
		
		elif msg['type'] == "RequestVote":
			handle_request_vote(msg)

		elif msg['type'] == "RequestVoteResponse":
			handle_request_vote_response(msg)
   
		elif msg['type'] == "AppendEntries":
			handle_append_entries(msg)

		elif msg['type'] == "AppendEntriesResponse":
			#print(str(my_id) + " RECEIVED APPEND ENTRIES RESPONSE: SUCCESS? -> " + str(msg["success"]))
			handle_append_entries_response(msg)

	clock = time.time()

	if clock-lastEvent > electionTimeout/2 and thisRole == "leader":
		lastEvent = clock
		sendHeartbeat()
		

	if clock-lastEvent > electionTimeout:
		lastEvent = clock
		if thisRole == "follower":
			begin_election()
			

		# # Send a no-op message to a random peer every two seconds, just for fun
		# # You definitely want to remove this from your implementation
		# msg = {'src': my_id, 'dst': random.choice(replica_ids), 'leader': 'FFFF', 'type': 'noop'}
		# sock.send(json.dumps(msg))
		# print(msg['src'] + ' sending a NOOP to ' + msg['dst'])
		# last = clock
