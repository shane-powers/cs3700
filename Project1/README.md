# Overview
The purpose of this project is to orient ourselves with writing simple network code. We were tasked with implementing a client program to 
communicate with a server using sockets. Along with string manipulation and counting, and successfully ‘talking’ to the server, we are 
able to decipher a secret code to hold as a trophy for completion of the assignment. Furthermore, as extra credit, we are able to find 
an additional secret code by talking to the server over a more secure SSL connection. Using Python I was able to accomplish the main task, 
as well as the extra credit assignment. 

# Challenges Faced
Right out of the gate, my first dilemma was reteaching myself the Python programing language. I study CE/CS and most of my coursework is in 
Java and C++. I am also fresh out of co-op where I was using primarily Java and JavaScript with Typescript and React. Instead of reaching 
for a language I was already familiar with, I went with Python which I knew I would be able to pick up quickly, but still wanted to become 
more comfortable with. After getting a handle of the syntax again (which happened from project start all the way through project completion) 
my next hurdle was correctly parsing the data received from the server. Python documentation made it pretty easy to establish a connection 
to the server given the IP and the Port Number, but I had to figure out how to encode my messages and decode the messages received. 
After I figured that out, it was easy to figure out how to implement logic with the returned message from the server in order to find 
the secret code. Most of my challenge came from the extra credit assignment. Mostly, this extra assignment shined the light on a major 
bug in my code. I was parsing only a partial message received from the server. It took some time for me to figure out a way to make sure 
I received the full message from the server, which required a loop to call `.recv(8192)` several times and stop only when my received data 
encountered the end of line character (which was most difficult because I had to understand when and why I needed to encode and decode). 

# Testing Method
## Language
In the beginning, most of my testing was revolving around Python `print` statements as I was busy wrapping my head around the Python language 
for the first time in a long time. This testing was based around trying to run my code and seeing where I hit an exception or tried to implement 
a method on a string I knew existed in JavaScript but was not called the same thing in Python. These tests lasted the full length of the project 
as I was learning Python as a language throughout. 
## Talking to Server
Once I had an established connection with the server, my testing then turned to making sure my code communicated correctly with said server. 
Using many, many `print` statements for my messages before I sent them to the server, as well as printing out the data I received from the server 
before I tried to parse it, I made sure I was working with the information as I was supposed to. Throughout the process, I used several `if` 
statements or `try` and `catch` methods to make sure that errors were caught immediately and didn’t spill into the next ‘level’ of logic in my 
program. This testing was a lot of mock data sent to my methods seeing how they would react and making sure they raised an error, or the correct 
return value when expected. 
## Arguments 
Finally, towards the conclusion of this project, I extrapolated the constants I defined and raised them up to be arguments into my program. 
This immediately caused several ways for errors to be introduced to my application. If the incorrect number of arguments is passed in, or an 
incorrect argument, or an unrecognized flag. Because of many of these unknowns, I doubled down on the `try` and `catch` statements and made 
sure through other logics that the arguments and flags were being interpreted as they were supposed to. I probed my program with many different 
variation of inputs, both correct and incorrect, too few and too many, recognized and unrecognized, and made sure that my program handled them 
all as expected. 

