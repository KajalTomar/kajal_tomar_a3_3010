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
from classes.peer import Peer

# variables to hold host, port numbers
HOST = ""
WELL_KNOWN_PEERS = ["silicon.cs.umanitoba.ca","eagle.cs.umanitoba.ca"];
PEER_NETWORK_PORT = 16000
MY_PORT = 8395
# 8395 8399
# set up the socket for the clients

hostname=socket.gethostname()
IPAddr=socket.gethostbyname(hostname)

wellKnownPeerSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

peerSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
peerSocket.bind((HOST, MY_PORT))
peerSocket.setblocking(0)

inputs = [peerSocket]
outputs = []
exceptions = []

myPeers = []
# --------------------------------------------------------------------------
# calcTimeout()
#
# Purpose: calculates the timeout based on the current nearest due date
# Returns: the timeout
# --------------------------------------------------------------------------
def calcTimeout():
	timeout = 60;
	# timeout = closestDueDate - time.time() (current time)
	return timeout;

# --------------------------------------------------------------------------
# gossip()
#
# Purpose: sends a GOSSIP message to enter, and stay active in the network
# --------------------------------------------------------------------------
def gossip():
	theMessage = json.dumps({'command': 'GOSSIP', 'host':IPAddr, 'port': MY_PORT, 'name':'potato', 'messageID': str(uuid.uuid4())})
	print(theMessage)
	wellKnownPeerSocket.sendto(theMessage.encode('utf-8'),(WELL_KNOWN_PEERS[0], PEER_NETWORK_PORT)) # udp message	
	wellKnownPeerSocket.sendto(theMessage.encode('utf-8'),(WELL_KNOWN_PEERS[1], PEER_NETWORK_PORT)) # udp message	

# --------------------------------------------------------------------------
# parseMessage(message)
#
# Purpose: parse the message sent by a peer in the network
# Parameter: the message
# --------------------------------------------------------------------------
def parseMessage(message, heardAt):
	message = message.decode('utf-8') ## note message[2] has the address of the sender
	message = json.loads(message)
#	print(message)
	# ignore invalid messages (all valid messages have a command key)
	if("command" in message):
		if(message["command"] == "GOSSIP" or  message['command'] == 'GOSSIP'):
			print(message)
		if(message["command"] == "GOSSIP_REPLY" or  message['command'] == 'GOSSIP_REPLY'):
			gossipReplyHeard(message, heardAt)

# --------------------------------------------------------------------------
# gossipReplyHeard()
#
# Purpose: a peer sent a gossip_reply. If they aren't in the peer list,
#	then add them to it
# Parameter: the message, time it was recieved
# --------------------------------------------------------------------------
def gossipReplyHeard(message, heardAt):
	if(("host" in message) and ("port" in message) and ("name" in message)):
		# the message is valid
		tempPeer = Peer(message["host"],message["port"],message["name"],heardAt)
		
		for aPeer in myPeers:
			if(aPeer != tempPeer):
				myPeers.append(tempPeer)

def printAllPeers():
	for aPeer in myPeers:
		print(aPeer)

def main():
	# first time announcement
	gossip()

	while True:
		try:
			readable, writable, exceptional = select.select(inputs, outputs, exceptions, calcTimeout())
			
			for s in readable:
				if s is peerSocket:
					# check the socket for the peers and handle the messages
					data = s.recv(1024)
					if(data):
						parseMessage(data, time.time())
			
			for s in exceptions:
				print('closing socket for '+s.getpeername()+' due to an exception.')
				s.close()

			if not (readable or writable or exceptional):
				print('------------------------------------------')
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
