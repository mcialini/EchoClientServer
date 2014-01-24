#!/usr/bin/env python

"""-----------------------------------------------------------------------------------------------------------------------------------------------
Full Echo Server by Matt Cialini

This server will will bind a socket to the port number input by the user on the local machine. It then will listen for a client program, accept 
an incoming connection request, and start receiving data. It will then split up the message into variables that are checked for validity based on
our defined protocol. If the message contains some part which is not valid, the server will send an error message to the client and then break the 
connection. If the message is valid, the server will then wait for the amount of time specified by the client, then echo the message back. Once a
terminate message is received, it will peacefully close the connection.

-----------------------------------------------------------------------------------------------------------------------------------------------"""

import socket
import sys
import string
import time

host = ''
port = int(sys.argv[1])
backlog = 5
msg = []
phase = ''
mType = ''
incomingProbes = 0
header = 1 + 1 + 4 + 1 + 4 + 1 + 4 + 1 + 4 	# payloadSize of setup message header
size = 0	
delay = 0.0
probesReceived = 0

def setup(msg):
	#print msg
	if len(msg) != 5:
		return False
	try:
		global phase, mType, incomingProbes, size, delay, header
		phase = msg[0]
		mType = msg[1]
		if mType != "rtt" and mType != "tput":
			return False
		incomingProbes = int(msg[2])
		size = int(msg[3])
		if size == 0: # size = 0 indicates that user wants to automate either measurement for all specified output sizes, so start at lowest for that mType
			if mType == "rtt":
				size = 1
			elif mType == "tput":
				size = 1000		
		delay = float(msg[4])
		header = 1 + 1 + 1 + 1 	# assume that a mType msg will always follow a setup msg, so make the header size equal to the number of bytes to expect before the payload
		return True
	except ValueError:
		return False
		

# Initialization statement
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((host,port))
s.listen(backlog)
client, address = s.accept()
# Connection has been established to the client, begin loop
while 1:
	data = ""
	
	# size of measurement header will need to be incremented
	if (probesReceived + 1) == 10:
		header += 1
	if (probesReceived + 1) == 100:
		header += 1
	
	# To assure that the full message is received, loop on client.recv until the expected message size is fully received.	
		
	while len(data) < header+size:		
		data += client.recv(1000)
		# no need to keep looping
		if data[0] == 's':
			break
		if data[0] == 't':
			break
	msg = string.split(data, ' ')	
	if msg[0] == 's':
		probesReceived = 0	# reset the count
		if setup(msg) is False:
			client.send("404 Error: Invalid Connection Setup Message")
			client.close()
			break
		else:
			client.send("200 OK: Ready")
	elif msg[0] == 'm':			# message count begins at 1 
		probesReceived += 1		
		if len(msg) != 3:
			client.send("1404 Error: Invalid Measurement Message")
			client.close()
			break
		else:
			try:
				phase = msg[0]
				probeNum = int(msg[1])
				# checks if the probes are received in the correct order
				if probeNum != probesReceived:
					client.send("2404 Error: Invalid Measurement Message")
					client.close()
					break
				# checks if an extra measurement message has been received
				if probeNum > incomingProbes:
					client.send("3404 Error: Invalid Measurement Message")
					client.close()
					break
				payload = msg[2]
			except ValueError:
				client.send("4404 Error: Invalid Measurement Message")
				client.close()
				break
			time.sleep(delay)	# delay the echo for "delay" seconds
			client.send(" ".join(msg))
			print "Successfully echoed probe " + str(probeNum)
			if probeNum == incomingProbes: # if received the final Measurement message, reset insizes to accept a setup message
				header = 1 + 1 + 4 + 1 + 4 + 1 + 4 + 1 + 4	
				size = 0
	elif msg[0] == 't':
		if len(msg) > 1 and msg[1] == "":	# because format is <t><ws>, msg should have empty string in second pos
			client.send("200 OK: Closing Connection")
		else:
			client.send("404 Error: Invalid Connection Termination Message")
		client.close()
		break
	else:
		client.send("404 Error: Invalid Protocol Phase")
		client.close()
		break

				

	

	
