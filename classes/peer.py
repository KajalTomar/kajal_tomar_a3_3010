import json

class Peer:

	# constructor 
	def __init__(self, host, port, name):
		self.host = host
		self.port  = port
		self.name = name

	# so I can print the peer's information
	def __str__(self):
		 return json.dumps({"host":host, 
				 "port": port, 
				 "name":name})
	
	
