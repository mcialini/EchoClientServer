#!/usr/bin/env python

"""-------------------------------------------------------------------------------------------------------------
A simple echo client by Matt Cialini

This client program will accept a hostname and a port number from the command line which it will use to connect 
to the server program. Once the connection has been accepted by the server, the client prompts the user for a 
string which it then sends to the server program. It then receives back a message, prints it, and terminates the 
connection.

-------------------------------------------------------------------------------------------------------------"""

import socket
import sys

host = sys.argv[1]
port = int(sys.argv[2])
size = 4096
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((host,port))
msg = raw_input("Type your message:")
s.send(msg)
data = s.recv(size)

print 'Received:', data
s.close()
