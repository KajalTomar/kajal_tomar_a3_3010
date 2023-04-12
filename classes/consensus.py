import json
import copy

class Consensus:

	# constructor 
	def __init__(self, om, index, value, peers, messageID, due, ogMessageID, ogSender):
		self.om = om
		self.index = index
		self.value = value
		self.peers = peers
		self.messageID = messageID
		self.due = due
		self.ogMessageID = ogMessageID
		self.ogSender = ogSender
		self.replyAmount = 0
		self.values = [value]

	# so I can print the consensus's information
	def __str__(self):
		return json.dumps({"om":self.om, 
				"index": self.index, 
				"value": self.value,
				"peers": self.peers,
				"messageID": self.messageID,
				"due": self.due
				},indent=4) 

	def getMsg(self):	
		return json.dumps({"om":self.om, 
				"index": self.index, 
				"value": self.value,
				"peers": self.peers,
				"messageID": self.messageID,
				"due": self.due
				}).encode('utf-8')

	def gotResponse(self, val):
		replyAmount = replyAmount + 1
		if(val):
			allValues.append(val)

	def mostHeard(self):
		if(len(self.values) > 0):
			return max(set(self.values), key=(self.values).count)
		else:
			return -1
	
	def everyoneReplied(self):
		if(replyAmount == len(peers)):
			return True
		else:
			return False
