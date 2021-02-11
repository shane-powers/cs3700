# High-level Approach
Starting off the project, I immediatly began the parsing of the arguments to be sent to this application. I knew from the previous assignment that I knew how to send and recieve data from sockets so the biggest step, in my mind, was to be able to parse the arguments sent to the program to know what data to send to what sockets. After that it was just a matter of what logic to carry out and when. 

Off this initial approach, I quickly realized I fell in line with the 'Suggested Implementation Approach' found in the assignment overview:
1) Command Line Parsing
2) Connection Establishment
3) MKD and RMD
4) PASV and LIST
5) STORE, RETR, and DELE

Much of the work in the later steps was already accomplished in my steps 1 and 2. I added a switch block based off of the command recieved as an argument and inside that swith block, I was able to call the respective command to the FTP server that it was expecting to carry out the expected command. Outside and before this switch block were many methods to create to and connect to sockets, send and recieve messages from local files and the FTP server over sockets, and the methods to parse the URL argument mentioned earlier. Before this switch statement is also where I established the control socket to talk with the FTP server. 

# Challenges Faced
## Argument Parsing
It was difficult to come up with a clean, efficient method to parse a URL argument. I tried three different methods of parsing this URL, and settled on using python's `.parse()` method to separate the URL on specific characters. The core logic was to separate on the '@' symbol, if the resulting array had one item, it was just the host and optional port, if there were two items, it was the username and optional password and the host and optional port, if there were three items there was an error and I exited with 1. I used similar logic for the user and password and the host and port, and eventually had a username, password, hostname, port number, and path to use in the remainder of the application.

Further, I tried to parse both arguments (if there were two) as URLs. If both of them succeeded, I returned an error, and if neither were URLs, it would return an error. It would succeed if one argument was a URL, and I assumed that the other argument had to be a path to a local directory/file. 

## Data Socket
After parsing the arguments, I was very easily able to implement the `mkdir`, `rmdir`, and `rm` commands on our FTP client. The next hurdle came from opening the dataport to read and write information from the FTP server to our client. To accomplish this, I first abstracted the create and connect to socket methods so that I can use them to create a new socket at will. I then created a method that automatically opens a data socket, reads or writes from that data socket, and returns the data (if reading). This data can then be passed along to whereever it needs to go.

The problems faced here were knowing when all the data has been recieved from the data port, as well as parsing the servers response to the `PASV` command to know what IP and on what port the server is opening a data socket. After some time I was able to come up with the logic necessary to complete the methods for the data socket, namely add a `time.wait()` call to slow down the execution of our program and give the server time to think/send data and for us to recieve that data. 

## Local File IO
Finally, to wrap up the assignment, I had to brush the dust off of using python to read and write from a local file. I did not know what to do here at first, but followed my method structure of reading and writing from FTP, and made methods to read and write from a local file. I had to check that the file did actually exist if I expected it to before proceeding, but that was not too hard. It was largely the same issue of knowing when I was done reading or writing to a file, so that I can close that open stream.

# Overview of Testing
For testing, with the FTP server itself it was a lot of trial and error. I would send a message to the FTP server and see what reply I would get. Same with the data stream, I was messing around with the `ls` command a ton, making new files and making sure they were successfully being listed. A lot of the tests performed here were as I was creating different components, I would confirm the expected behavior of sending a method or this application valid, as well as invalid data. 

Additionally, I was using an external python interpreter to test my parsing of different variations of URLs, whether or not they had a username, or a password, or a port, or if they were just invalid for missing expected delimiters or the hostname or path. I also used an external pyton interpreter to test the correct parsing of the IP and Port returned for the data socket. 