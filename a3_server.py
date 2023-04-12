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

GOSSIP_INTERVAL = 60
WORD_SIZE = 5;

# variables to hold host, port numbers
HOST = ""
WELL_KNOWN_PEERS = ['silicon.cs.umanitoba.ca','eagle.cs.umanitoba.ca','hawk.cs.umanitoba.ca','osprey.cs.umanitoba.ca'];
PEER_NETWORK_PORT = 16000
MY_PORT = 8396
MY_NAME = 'potato'
# 8395 8399
# set up the socket for the clients
WHITELISTED_PEERS = [('130.179.28.119',16000),('130.179.28.126',16000),('130.179.28.37',16000),('130.179.28.113',16000)]
hostname=socket.gethostname()
MY_HOST=socket.gethostbyname(hostname)

wellKnownPeerSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

peerSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
peerSocket.bind((HOST, MY_PORT))
peerSocket.setblocking(0)

inputs = [peerSocket]
outputs = []
exceptions = []

myPeers = []
allMessages = [] # messageIDs of all messages ever heard
theWords = ['','','','','']


theAnnouncement = json.dumps({'command': 'GOSSIP', 'host':MY_HOST, 'port': MY_PORT, 'name':MY_NAME, 'messageID': str(uuid.uuid4())})
lastGossipTime = 0;

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
	global lastGossipTime;
	currentTime = time.time()
	
	if((currentTime - lastGossipTime) >=  GOSSIP_INTERVAL):
		lastGossipTime = currentTime
		for aPeer in WELL_KNOWN_PEERS:
			wellKnownPeerSocket.sendto(theAnnouncement.encode('utf-8'),(aPeer, PEER_NETWORK_PORT)) # udp message	
		print(theAnnouncement)

# --------------------------------------------------------------------------
# parseMessage(message)
#
# Purpose: parse the message sent by a peer in the network
# Parameter: the message
# --------------------------------------------------------------------------
def parseMessage(data, heardAt):
	message = data[0].decode('utf-8') ## note message[2] has the address of the sender
	message = json.loads(data[0])
#	print(message)
	if(data[1] in WHITELISTED_PEERS):		 # delete before handin
		# ignore invalid messages (all valid messages have a command key)
		if("command" in message):
			if((message["command"] == "GOSSIP") and ("host" in message) and ("port" in message) and ("name" in message) and ("messageID" in message)):
				gossipHeard(message, heardAt)
			if((message["command"] == "GOSSIP_REPLY") and ("host" in message) and ("port" in message) and ("name" in message)):
				gossipReplyHeard(message, heardAt)
			if((message["command"] == "SET") and ("index" in message) and ("value" in message)):
				setHeard(message)

# --------------------------------------------------------------------------
# gossipReplyHeard()
#
# Purpose: a peer sent a gossip_reply. If they aren't in the peer list,
#	then add them to it
# Parameter: the message, time it was recieved
# --------------------------------------------------------------------------
def gossipReplyHeard(message, heardAt):
	print(message)
	addIfNewPeer(message, heardAt)


# --------------------------------------------------------------------------
# gossipReplyHeard()
#
# Purpose: a peer sent a gossip_reply. If they aren't in the peer list,
#	then add them to it
# Parameter: the message, time it was recieved
# --------------------------------------------------------------------------
def gossipHeard(message, heardAt):
	addIfNewPeer(message, heardAt)

	# ignore if someone sent my own gossip message back to me
	if(message["name"] != MY_NAME and message["host"] != MY_HOST and message["port"] != MY_PORT):
		msgID = message["messageID"]

		# if this message has never been heard before
		if((len(allMessages) == 0) or (msgID not in allMessages)):
			allMessages.append(msgID)
		
			#print('sending message '+msgID)

			# forward the message verbatim to 3-4 random peers
			if(len(myPeers) > 3):
				randomPeers = random.sample(myPeers, 4) 
				#print('RANDOM PEERS:')
				#print(randomPeers)

				# send the exact message to 3-4 peers 
				for aPeer in randomPeers: 
					if(aPeer.name != message["name"] and aPeer.host != message["host"] and aPeer.port != message["port"]):
						wellKnownPeerSocket.sendto((json.dumps(message)).encode('utf-8'), (aPeer.host, aPeer.port)) # udp message	
			elif(len(myPeers) > 0): # if there are 3 or less peers, then have to send it to them
				for aPeer in myPeers:	
					if(aPeer.name != message["name"] and aPeer.host != message["host"] and aPeer.port != message["port"]):
						wellKnownPeerSocket.sendto((json.dumps(message)).encode('utf-8'), (aPeer.host, aPeer.port)) # udp message	

			# reply to the original sender
			theReply = json.dumps({'command': 'GOSSIP_REPLY', 'host':MY_HOST, 'port': MY_PORT, 'name':MY_NAME})
			wellKnownPeerSocket.sendto((json.dumps(theReply)).encode('utf-8'), (message["host"], message["port"])) # udp message	
							

# --------------------------------------------------------------------------
# setHeard(message)
#
# Purpose: set index of theWords to the given value
# Parameter: the message
# --------------------------------------------------------------------------
def setHeard(message):
	print(message)
	i = message["index"]
	val = message["value"]
	
	if(i >= 0 and i < WORD_SIZE and val):
		theWords[i] = val
	
	#printAllWords()

# --------------------------------------------------------------------------
# addIfNewPeer()
#
# Purpose: add peer to peer list if this is the first time hearing from them
# Parameter: the message
# --------------------------------------------------------------------------
def addIfNewPeer(message, heardAt):
	newPeer = 1;
	if(("host" in message) and ("port" in message) and ("name" in message)):
		# the message is valid
		tempPeer = Peer(message["host"],message["port"],message["name"],heardAt)
		
		if(tempPeer.name != MY_NAME and tempPeer.host != MY_HOST and tempPeer.port != MY_PORT):
			if(len(myPeers) == 0):
				myPeers.append(tempPeer)
			else:
				for aPeer in myPeers:
					if(aPeer == tempPeer):
						newPeer = 0
						break
				if(newPeer == 1):
					myPeers.append(tempPeer)
		
	#		printAllPeers()

# --------------------------------------------------------------------------
# printAllWords()
#
# Purpose: prints all the words
# --------------------------------------------------------------------------
def printAllWords():
	print('-------------------------------')
	for word in theWords:
		print('> '+ word)
	print('-------------------------------')

# --------------------------------------------------------------------------
# printAllPeers()
#
# Purpose: prints all the peers
# --------------------------------------------------------------------------
def printAllPeers():
	print('-------------------------------')
	for aPeer in myPeers:
		print(aPeer)
	print('-------------------------------')


def main():
	global lastGossipTime
	# first time announcement
	gossip()

	while True:
		print('OUTSIDE LOOP')
		try:
			readable, writable, exceptional = select.select(inputs, outputs, inputs, 60)
		
			for s in readable:
				gossip()
				
				if s is peerSocket:
					# check the socket for the peers and handle the messages
					data = s.recvfrom(1024)
					if(data):
						parseMessage(data, time.time())
				else:
					print('some other type of socket---------------------------------------')
					# check the socket for the peers and handle the messages
					data = s.recvfrom(1024)
					if(data):
						parseMessage(data, time.time())
			if not (readable or writable or exceptional):
				# timed out, so gossip
				#	gossip()
				print('1:*********************TIMEOUT***********************');
				if len(allMessages) > 120:
				    myList = allMessages[:100]
			#	continue 
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
