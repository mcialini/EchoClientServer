#!/usr/bin/env python

"""
Full Echo Client by Matt Cialini

This client program will accept a hostname and a port number from the command line which it will use to connect 
to the server program. Once the connection has been accepted by the server, the client prompts the user for a message to send. This message is expected 
to be a setup message, and if it is valid, the client will move on to its measurement phase. It will automate either the round trip time or throughput
measurement based on the paramaters specified by the user. Once a termination message is sent to the server, both the server and client close the 
connection.
"""

import socket
import sys
import string
import time

host = sys.argv[1]
port = int(sys.argv[2])
mType = ''
inSize = 1000 	# to assure the entire message is received back
data = ""
loop = True

# Initiates the connection to the server
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((host,port))

# Calculates average throughput based on the outsize and number of probes specified
def tput(outSize, numProbes):
	throughputs = []
	for i in range (1,numProbes+1):
		message = "m " + str(i) + " " + ("a"*outSize)
		timeSent = time.time()	# time.time() returns a value in seconds
		s.send(message)
		resp = ""
		# assure that no part of the message is lost
		while len(resp) < len(message):
			resp += s.recv(inSize)
		timeReturned = time.time()
		if resp != message:
			return -1
		throughputs.append((outSize/1024.0)/(timeReturned-timeSent)) # calculation for throughput in KB/s
		print "Probe " + str(i) + ": " + str((timeReturned-timeSent)*1000) + "ms, " + str(throughputs[len(throughputs)-1]) + "KBps"
	avg = sum(throughputs)/len(throughputs)
	print "Average for size = " + str(outSize) + ": " + str(avg) + "KBps"
	return avg

# Calculates average round trip time based on the outsize and number of probes specified
def rtt(outSize, numProbes):
	times = []
	for i in range (1,numProbes+1):
		message = "m " + str(i) + " " + ("a"*outSize)
		timeSent = time.time()
		s.send(message)
		resp = ""
		# assure that no part of the message is lost
		while len(resp) < len(message):
			resp += s.recv(inSize)
		timeReturned = time.time()
		if resp != message:
			return -1
		times.append((timeReturned-timeSent)*1000) # calculate round trip time in ms
		print "Probe " + str(i) + ": " + str(times[len(times)-1]) + "ms"
	avg = sum(times)/len(times)
	print "Average for size = " + str(outSize) + ": " + str(avg) + "ms"
	return avg
	
	
	 
# Automatically runs tput for all sizes to easily generate graph	
def tputAuto(numProbes,delay):
	outSize = 1000, 2000, 4000, 8000, 16000, 32000
	numSizes = len(outSize)
	averages = []
	for h in range (0,numSizes):
		next = tput(outSize[h], numProbes)
		if next == -1:
			print "Echo mismatch"
			return -1			
		averages.append(next)	# tput will return the avg tput for a single outsize
		if h < (numSizes-1):	# if we have calculated the tput for the largest size, we should not send another setup message
			msg = "s tput " + str(numProbes) + " " + str(outSize[h+1]) + " " + str(delay)
			s.send(msg)
			inmsg = s.recv(inSize)
			if inmsg != "200 OK: Ready":
				return -1
	print averages
	return 1
	
	
	
# Automatically runs rtt for all sizes to easily generate graph	
def rttAuto(numProbes,delay):		
	outSize = 1, 100, 200, 400, 800, 1000
	numSizes = len(outSize)
	averages = []
	for h in range (0,numSizes):
		next = rtt(outSize[h], numProbes)
		if next == -1:
			print "Echo mismatch"
			return -1
		averages.append(next)	# rtt will return the avg rtt for a single outsize
		if h < (numSizes-1):	# if we have calculated the rtt for the largest size, we should not send another setup message	
			msg = "s rtt " + str(numProbes) + " " + str(outSize[h+1]) + " " + str(delay)
			s.send(msg)
			inmsg = s.recv(inSize)
			if inmsg != "200 OK: Ready":
				return -1
	print averages
	return 1

	
	
	
while loop:
	msg = raw_input("Type your message:")
	msgSplit = string.split(msg, " ")	# store array of information for later use
	s.send(msg)
	data = s.recv(inSize)
	print "Received: ", data
	if data == "200 OK: Ready":
		# don't need to catch exceptions because the server has already verified a proper format
		mType = msgSplit[1]
		numProbes = int(msgSplit[2])
		outSize = int(msgSplit[3])
		delay = float(msgSplit[4])
		# design decision to automatically run for all sizes if the size element in the setup message = 0
		if mType == "rtt":
			if outSize == 0:	
				if rttAuto(numProbes,delay) == -1:
					s.close() 
					loop = False
			else:
				if rtt(outSize, numProbes) == -1:
					s.close()
					loop = False
		elif mType == "tput":
			if outSize == 0:
				if tputAuto(numProbes,delay) == -1:
					s.close()
					loop = False
			else:
				if tput(outSize, numProbes) == 1:
					s.close()
					loop = False
	elif data == "200 OK: Closing Connection":
		s.close()
		loop = False
	else:	# received invalid message, so break out of loop
		s.close()
		loop = False
		


