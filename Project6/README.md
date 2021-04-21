# High Level Approach
To start this assignment, we both reviewed the Raft pdf document. We found this document to be very informative, and were able to develop a basic understanding of the protocol from it. We attempted to design our program to follow the Raft consensus algorithm summary given in the pdf. We began by implementing a basic leader election process. We set an abitrary timeout length, and made replicas check for a timeout in the while loop. If a timeout occured, that replica would initiate an election and send RequestVote messages to all of the other replicas. The other replicas would then check if the term in the RequestVote message was greater than or equal to the replicas current term. If that was the case, the replica then would reply with a vote. If the current candidate received a vote from the majority of the other replicas, it would make itself leader. After being elected, the leader sends heartbeat messages in the form of an AppendEntries with an empty entries field. This just serves to let the other replicas know that they are followers. When a replica that is not a leader receives a command from a client, it redirects the message to the leader. When a leader receives a put command, it puts the key value into storage, and sends out an AppendEntries message with the key value pair that was just entered into the log.

# Challenges Faced
For the milestone, we overcame many overhead issues, such as understanding the starter code provided to us, taking a ton of time to understand the Raft consensus algorithm in general, as well as writing a program in python to match our understanding of the algorithm we are looking to implement. Many of the challenges we faced were quickly able to be overcome with the use of print statements to track the flow of data and information across and between our nodes. We had to figure out what the purpose of the log was, and how our nodes should communicate information between each other whether that be a request vote, append entry, or a response from the leader to one of those two messages. We also had to handle get and put messages correctly and it took us time to understand how redirections work, and it turned out it was painfully easy, just a reflection back to the client. When we figured that out, and ran our code with print statements on the khoury machine, everything came together and we just had to diagnose issues as we saw them at runtime.

# Testing Overview
To test, we primatrily relied on print statements. Our program is very saturated with print statements so we can track the state of every node, and what actions/events it is doing whether it is a follower, candidate or leader. This testing method required a intuitive understanding of the protocol and how it is supposed to function to make sure that the print statements we are receiving are in fact the events that we are expecting to happen, and in accordance with the Raft consensus algorithm.