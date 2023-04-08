import json

class Peer:
	
	# constructor 
	def __init__(self, host, port, name, lastHeardAt):
		self.host = host
		self.port  = port
		self.name = name
		self.lastHeard = lastHeardAt

	# so I can print the peer's information
	def __str__(self):
		 return json.dumps({"host":self.host, 
				 "port": self.port, 
				 "name":self.name})

	# two peers are equal if they have the same host, port and name
	def __eq__(self, other):
		if((other.host == self.host) and (other.port == self.port) and (other.name == self.name)):
			return True
		else:
			return False
	
