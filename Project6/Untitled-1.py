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
	return random.uniform(.6, 1)

############################# PERSISTENT STATE ON ALL SERVERS
currentTerm = 0
votedFor = None
log=[{'term': 0, "action": None, "value": None}]

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
		send_msg(msg)
		return
	elif votedFor == None or votedFor == candidateId or term > currentTerm:
		#grant vote
		votedFor = candidateId
		msg = {'src': my_id, 'dst': candidateId, 'type': 'RequestVoteResponse', "leader": currentLeader, 'data': True}
		send_msg(msg)
		return
	else:
		msg = {'src': my_id, 'dst': candidateId, 'type': 'RequestVoteResponse', "leader": currentLeader, 'data': False}
		send_msg(msg)
		return

############################# APPEND ENTRIES RPC METHOD
def append_entries_rpc(term, leaderId, prevLogIndex, prevLogTerm, entries, leaderCommit):
	global log, my_id, lastEvent, currentLeader, currentTerm
	lastEvent = time.time()  
	#print(str(my_id) + " RECEIVED APPEND ENTRIES FROM " + str(leaderId))
	if prevLogIndex >= len(log) or term < currentTerm or prevLogTerm != log[prevLogIndex]["term"]:
		msg = {'src': my_id, 'dst': leaderId, 'type': 'AppendEntriesResponse', 'nextIndex': len(log), "term":currentTerm, "leader": currentLeader, 'success': False}
		send_msg(msg)
		return
	
	else: #log[prevLogIndex] == prevLogTerm: # TODO CATCH ERROR OUT OF BOUNDS INDEX
		for entry in entries:
			STORE[entry["key"]] = entry["value"]
			log.append(entry)
		msg = {'src': my_id, 'dst': leaderId, 'type': 'AppendEntriesResponse', 'nextIndex': len(log), "term":currentTerm, "leader": currentLeader, 'success': True}
		send_msg(msg)
		currentLeader = leaderId
		currentTerm = term
	
		return
	if(leaderCommit > commitIndex):
		commitIndex = min(leaderCommit, len(log)-1)

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
	#print(str(my_id) + " BECAME A CANDIDATE AND INCREASED ITS TERM. CURRENT TERM: " + str(currentTerm))
	votedFor = my_id
	data = {
		'term': currentTerm,
		'candidateId': my_id,
		'lastLogIndex': len(log) - 1,
		'lastLogTerm': log[len(log)-1]['term']
	}
	msg = {'src': my_id, 'dst': "None", 'type': 'RequestVote', "leader": currentLeader, 'data': data} 
	send_to_all(msg)

def make_self_leader():
	global thisRole, currentLeader, receivedVotes
	#print(str(my_id) + " MADE ITSELF A LEADER")
	thisRole = "leader"
	currentLeader = my_id
	receivedVotes = []
	for rid in replica_ids:
		next_index_dict[rid] = len(log)
	sendHeartbeat()

############################# HANDLE RECEIVED MESSAGE METHODS
def handle_request_vote(msg):
	data = msg['data']
	request_vote_rpc(data['term'], data['candidateId'], data['lastLogIndex'], data['lastLogTerm'])
	
def handle_request_vote_response(msg):
	global thisRole, receivedVotes
	if thisRole == "candidate" and msg['dst'] == my_id:
		if msg['data'] == True:
			receivedVotes.append(msg['src'])
		if len(receivedVotes) > (len(replica_ids)-1)/2.0:
			make_self_leader() 

def handle_append_entries(msg):
	global thisRole
	if thisRole != "follower":
		thisRole = "follower"
	data = msg['data']
	append_entries_rpc(data["term"], data["leaderId"], data["prevLogIndex"], data["prevLogTerm"], data["entries"], data["leaderCommit"])

def handle_append_entries_response(msg):
	global currentTerm, next_index_dict, currentLeader
	if thisRole == "leader":
		# if currentTerm < msg['term']:
		# 	give_up_leader(msg['term'], msg["leader"])
		# 	return
		if msg['success'] == False:
			next_index_dict[msg["src"]] = msg["nextIndex"]
		elif msg['success'] == True:
			#success true
			next_index_dict[msg["src"]] = min(len(log), msg["nextIndex"])
	else:
		currentLeader = msg["leader"]
		currentTerm = msg["term"]
		

# goodResponse = {}
# def handle_append_entries_response(msg):
# 	global thisRole, goodResponse
	
# 	if thisRole == "leader":
# 		goodResponse[currentTerm].append(msg["src"])
# 	if len(goodResponse[currentTerm]) > len(replica_ids)/2.0:
# 			print("enough good responses")
# 	else:
# 		print("not enough good responses")

def handle_redirect(msg):
	msg = {'src': my_id, 'dst': msg["src"], "leader": currentLeader, 'type': 'redirect', 'MID': msg["MID"]}
	send_msg(msg)


def handle_get(msg):
	global commitIndex, log
	if(thisRole == "leader"):
		try:
			response = STORE[msg['key']] # will be a value or 'None'
		except:
			response = None	
		if response:
			reply = {'src': my_id, 'dst': msg["src"], "leader": currentLeader, 'type': 'ok', "MID": msg["MID"], "value": response} 
			send_msg(reply)
		else:
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
# 		'leaderCommit': commitIndex
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

	follow_prev_log_index = max(0, min(next_index_dict[rid]-1, len(log)-1))

	data = {
		'term': currentTerm,
		'leaderId': my_id,
		'prevLogIndex': follow_prev_log_index,
		'prevLogTerm': log[follow_prev_log_index]["term"],
		'entries': entries,
		'leaderCommit': commitIndex,
	}
	msg = {'src': my_id, 'dst': rid, 'type': 'AppendEntries', "leader": currentLeader, 'data': data}
	send_msg(msg)

def handle_put(msg):
	global commitIndex, log
	if thisRole == "leader":
		commitIndex += 1
		newLogEntry = {"term": currentTerm, "action": "PUT", "key":msg["key"], "value":msg["value"]}
		log.append(newLogEntry)
		
		for rid in replica_ids:
			send_append_entries_for_replica(rid)
		STORE[msg["key"]] = msg["value"]



		reply = {'src': my_id, 'dst': msg["src"], "leader": currentLeader, 'type': 'ok', "MID": msg["MID"]} 
		send_msg(reply)
	else:
		handle_redirect(msg)
	
############################# MAIN LOOP
while True:
	ready = select.select([sock], [], [], 0.1)[0]
	
	if sock in ready:
		msg_raw = sock.recv(32768)
		
		if len(msg_raw) == 0: continue
		msg = json.loads(msg_raw)
		
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
			handle_append_entries_response(msg)

	clock = time.time()

	if clock-lastEvent > .5 and thisRole == "leader":
		lastEvent = clock
		sendHeartbeat()
		

	if clock-lastEvent > electionTimeout:
		lastEvent = clock
		if thisRole != "leader":
			begin_election()