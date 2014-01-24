#!/usr/bin/env python

"""-------------------------------------------------------------------------------------------------------------
A simple echo server by Matt Cialini

This server program first accepts a port number from the command line which it then passes along with the 
local machine's address to bind the socket. Once the server is connected to by a client, it will continuously
listen for a message and accept a fixed number of bytes. After it receives the client's message, it echoes
the exact message back to the client.

------------------------------------------------------------------------------------------------------------"""

import socket
import sys

host = ''
port = int(sys.argv[1])
size = 4096
backlog = 5

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((host,port))
s.listen(backlog)

while 1:
    client, address = s.accept()
    data = client.recv(size)
    client.send(data)

client.close()
