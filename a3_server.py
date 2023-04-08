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
import traceback

# variables to hold host, port numbers
HOST = ""
WELL_KNOWN_PEERS = ["silicon.cs.umanitoba.ca","eagle.cs.umanitoba.ca"];
PEER_NETWORK_PORT = 16000
MY_PORT = 8396
# set up the socket for the clients

lastGossipTime = 0;

hostname=socket.gethostname()
IPAddr=socket.gethostbyname(hostname)

wellKnownPeerSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

peerSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
peerSocket.bind((HOST, 8396))
peerSocket.setblocking(0)

inputs = [peerSocket]
outputs = []
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
	wellKnownPeerSocket.sendto(theMessage.encode('utf-8'),(WELL_KNOWN_PEERS[0], PEER_NETWORK_PORT)) # udp message	
	wellKnownPeerSocket.sendto(theMessage.encode('utf-8'),(WELL_KNOWN_PEERS[1], PEER_NETWORK_PORT)) # udp message	

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
			timeout = 60

			readable, writable, exceptional = select.select(inputs, outputs, inputs, timeout)
			
			for s in readable:
				if s is peerSocket:
					# check the socket for the peers and handle the messages
					data = s.recvfrom(1024)
					if(data):
						parseMessage(data)
					
			if not (readable or writable or exceptional):
				# timed out, so gossip
				gossip()
				continue 
		
		except KeyboardInterrupt as e:
			print("End of processing.")
			sys.exit(0)
		except Exception as e:
			print(e)
			traceback.print_exc()
			print("End of processing.")
			peerSocket.close()
			sys.exit(0)
main();
