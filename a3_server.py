# --------------------------------------------------------------------
# NAME		        : Kajal Tomar
# STUDENT NUMBER	: 7793306
# COURSE		    : COMP 3010
# INSTRUCTOR	    : Robert Guderian
# ASSIGNMENT	    : Assignment 3
#
# REMARKS:  
# --------------------------------------------------------------------

import sys
import select
import json
import socket
import time
import random
import uuid
import re

# variables to hold host, port numbers
HOST = ""
ROB = "silicon.cs.umanitoba.ca"
PEER_NETWORK_PORT = 16000
MY_PORT = 8396
# set up the socket for the clients

lastGossipTime = 0;

hostname=socket.gethostname()
IPAddr=socket.gethostbyname(hostname)

peerSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
mySocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
mySocket.bind((HOST, 8396))

# --------------------------------------------------------------------------
# gossip()
#
# Purpose: sends a GOSSIP message to enter, and stay active in the network
# --------------------------------------------------------------------------
def gossip():
	global lastGossipTime
#	print('old time: '+str(lastGossipTime))
	lastGossipTime = time.time()
#	print('new time: '+str(lastGossipTime))
	theMessage = json.dumps({"command": "GOSSIP", "host":IPAddr, "port": 8396, "name":"potato", "messageID": str(uuid.uuid4())})
	print(theMessage)
	peerSocket.sendto(theMessage.encode('utf-8'),(ROB, PEER_NETWORK_PORT)) # udp message	


# --------------------------------------------------------------------------
# parseMessage(message)
#
# Purpose: parse the message sent by a peer in the network
# Parameter: the message
# --------------------------------------------------------------------------
def parseMessage(message):
	message = message[0].decode('utf-8') ## note message[2] has the address of the sender
	print(message)

def main():
	global lastGossipTime
	
	while True:
		try:
			# gossip every minute.. implmented this way for now. Rob suggests using the timeout in the select statement (which I don't have yet)
			if(time.time()-lastGossipTime >= 60):  	
				gossip()
				
			# check the socket for the peers and handle the messages
			data = mySocket.recvfrom(1024)
			if(data):
				parseMessage(data)

		except KeyboardInterrupt as e:
			print("End of processing.")
			sys.exit(0)
		except Exception as e:
			print(e)
			print("End of processing.")
			peerSocket.close()
			sys.exit(0)
main();
