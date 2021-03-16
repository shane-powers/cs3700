# Router Implementation
## High-Level Approach
- We began by implementing support for revoke messages. Out of everything we had to do after the milestone, this was the most simple. We began by looking through the revoke packet message to determine which networks we had to revoke. After determining this, we removed any revoked networks from our forwarding table. 
- For the milestone, we were using a dictionary for our forwarding table. We realized that it would be much easier to work with a list because we would frequently be adding and removing elements. 
- We then had to forward the revoke packet. If the packet was received from a customer, we forwarded it to all other neighbors. If the packet was received fromn a peer or a provider, we only forwarded it to customers. We also added this functionality to our update function.
- We then had to handle the dropping of data packets when they were not profitable. We did this by checking to see if the destination of the packet was in our forwarding table. If it was, we went ahead and forwarded it. If not, we dropped the data packet.
- We then had to implement the longest common prefix algorithm. We did this by converting the networks to a binary string and iterating through them. As we incremented through them, we compared each bit. While doing this, we kept track of the longest common prefix we could find.
- The final and most difficult part was implementing the coalesce function. In this function, we took in a packet and compared it to every entry in our forwarding table. We compared every attribute of the packet to every attribute of each route in our forwarding table (ASPath, origin, etc...). If they matched, we then compared the binary strings of the networks of the route and the packet. If these matched, we were ready to coalesce. To coalesce, we created a new route that contained all of the attributes of the existing route in the forwarding table, except for the netmask. We modified the netmask by one bit, either up or down depending on the relation to the compared packet, and then added that to the new route. We then removed the existing route from the forwarding table, and called coalesce again with our new route. By doing this, we could see if the newly coalesced route would need to be coalesced again. If not, the route supplied to the function is added to the forwarding table.
- We then had to modify our implementation of route. Every time revoke is called, we empty our forwarding table and repopulate by calling coalesce on every entry in our updates table.

## Challenges Faced
- Most of our issues were from a lack of conceptual understanding when it came to the functions we were implementing. This made it particularly difficult to troubleshoot when we ran into issues. We both had to do our fair share of research on what was actually occurring.
- When we were implementing the coalesce function, we initially had trouble with what actually defined a numerical adjecent network. We initially assumed that this meant there could only be a difference of 1 between the two network addresses, but this was incorrect. We realized that we were being too specific with our definition of neighbor. This was a big issue that was preventing us from passing the 6-2 tests. After fixing this, we were able to pass them.

## Overview of tests
- Our testing for the final implementation was in a similar fashion to that of the milestone.

# Router Implementation Milestone

## High-Level Approach
- To get started, we followed the structure of the Python skeleton code we were provided, as well as the step by step order of completion provided to us in the project description. Based on this path of compoletion, we started with wrapping our heads around how the starter code worked and what functionality it initially provided us with. 
- Next, we implemented a switch case for ALL possible message types with filler data inside the provided `handle_packet()` method. We walked through the project description and added as many comments inside this switch statement and subsequent helper methods, to give documentation to the expectations of our router. 
- After the comments were in place, outlining all of the work that we had to do, we got started with properly handling an 'update' message recieved by our router. We did our best to follow documentation, but had to overcome some functional misunderstandings, as well as some problems encountered with writing in Python coming from JavaScript. Eventually, we were able to successfully store updates to our router, store those updates to our forwarding table, and forward those updates on to all of our neighbors. (in the future we will include functionality to only send to customers)
- Once we had successfully implemented update messages, we then started work on 'dump' messages. Again, we encountered some issues with sending JSON data over a socket in Python, but after we overcame this, it was very straightforward sending a 'table' message with our forwarding table back to the router who sent us a 'dump' message.
- To wrap up the milestone, we included functionality for the 'data' message. This was also relatively straighforward, as we just needed to use the `get_route()` method to and our stored updates, which have already been done, to find the proper neighbor to forward the data message along to to reach its destination. 

## Challenges Faced
### 1) Refamiliarization with Python
- Many of the frustrations and obstacles we faced during this assignement were due to our lack of familiarization with Python. Both partners came from other languages, and there are subtle nuances of Python that caused a headache upon interpretation. We constantly found ourselves going back to code whose logic we knew was sound, to fix syntax errors. At some point we added a Pylint pluggin to help identify issues before they cause a headache.

### 2) Understanding the Provided Starter Code
- The initial challenge we had to overcome was developing an understanding of the current state of the program in the starter code provided. The starter code gave us a ton of functionality but we had to identify the line in the sand where we had to begin our implementation on top of the provided foundation. This was not too bad, as the method, and variable names were very straightforward, and the starter code handled the interactions with sockets and the network argument sent to the router.
- Additionally, we needed to add an additional argument to the program starter code. The starter code was not equiped to handle an ASN input on the command line, so we had to add this functionality. 

### 3) Realizing the Expectations of a Router
- Even after following the project documentation to a 'T', we ran into some obstacles with what our router was supposed to out put and 'from' who and 'to' who. Through trial and error, as well as some Google research, we were able to understand how each of the current implemented messages worked, and make sure that we were sending the packet from the correct source, to the correct destination, and correctly modified the packet. One of the bigger issues here to overcome was appending our own ASN to the update messages we forwarded to our neighbors. That issue stumped us for a while as we thought the issue was with our source and destination addresses for the packet we sent.

### 3) Realizing Expectations of the Simulator
- For a while, we did not realize how to send double quotes over the socket to the simulator. This could also be seen as a Python issue, but we used several libraries and methods to convert a JSON to string, but stumbled into `json.dumps()` later than we would have liked to. 
- Additionally, the errors from the simulator can be quite ambiguous, so when we got an issue, it was hard to diagnose what actually caused the issue. Through time this became easier but in the beginning it was pretty frustrating.

## Overview of Tests
- Initially, many of the tests we ran were trial and error with the simulator. We would try to send some data, and would see if the simulator would return an error. We carried on this method of testing through the whole milestone, becasue it was the most direct in identifying if there was an issue in the message we were trying to send to the routers in the simulator.
- Many of the issues faced by the Python implementation of the router we were able to test in the command line using a Python interpreter. Especially with testing variations of string parsing or json dumping, we wrote our command on the command line before including it in our solution to see if we got the expected result. 
- So many print statements. At every step of completing the milestone, we had a print statment to show what we were sending, or receiving, or parsing to make sure it is exactly what we think it is. The simulator errors only went so far to tell us what was wrong or what we can do to improve, but our print statements never failed us. 
