# Echo server program
import hashlib
import random
import socket
import string
import sys
	
users = {"han": "solo", "darth": "vader", "yo": "da"}
accounts = {"han": 0.0, "darth": 0.0, "yo": 0.0}

def waitForClient(userInput):
	args = userInput.split() # split operators into pieces	
	if(args[0] != "bank-server"):
		print("Command invalid")
	else:
		HOST = ''
		PORT = int(args[1])
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # SOCK_STREAM for TCP
		s.bind((HOST, PORT)) # bind the socket to all sources coming to our port number
		s.listen(5) # accept 5 connections at a time in the queue
		while 1:
			conn, address = s.accept() # create the connection. use the conn object from now on instead of the s socket
			if debug:
				print "Connected to", address
			data = conn.recv(1024) 
			if data == "authentication request": # this should be the first message sent.
				# generate random challenge, send that to the client. from http://stackoverflow.com/questions/2257441/random-string-generation-with-upper-case-letters-and-digits-in-python
				challenge = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(64))
				if debug:
					print "Sending challenge to client at {0}".format(address) 
				conn.sendall(challenge)
				
				# next thing sent should be the user
				user = conn.recv(1024)
				if debug:						
					print "authenticating user", user
				
				if user in users.keys(): # check if user exists
					conn.sendall("valid user")
					# calculate MD5 hash and compare
					md5 = hashlib.md5()
					md5.update(user + users[user] + challenge)
					myAuth = md5.hexdigest()						
					theirAuth = conn.recv(1024)
					if debug:
						print "myAuth", myAuth
						print "theirAuth", theirAuth
					if myAuth == theirAuth:
						if debug:
							print "Successful login. Sending notification to client"
						conn.sendall("login success")
						# get action to take on account
						action = conn.recv(1024)
						opAndNums = action.split(":")
						# validate the action
						if len(opAndNums) == 2:
							if debug:
								print "correct action sequence"
							operation = opAndNums[0]
							try:
								amount = float(opAndNums[1])
								if operation == "deposit":
									accounts[user] += amount
									if debug:
										print "Deposited money. Sending new balance to client at {0}".format(address)
									conn.sendall(str(accounts[user]))
								elif operation == "withdraw":
									if accounts[user] >= amount:
										accounts[user] -= amount
										if debug:
											print "Withdrew money. Sending new balance to client at {0}".format(address)
										conn.sendall(str(accounts[user]))
									else: # check for insufficient funds
										accounts[user] = 0
										if debug:
											print "Insufficient funds. Sending balance of $0.00 to client at {0}".format(address)
										conn.sendall("insufficient funds")
								else: # operation was not deposit or withdraw
									if debug:
										print "Invalid operation {0}. Sending error to client at {1}".format(operation, address)
									conn.sendall("invalid operation")
							except ValueError: # amount NaN
								if debug:
									print "ValueError when trying to parse {0}. Sending error to client at {1}".format(opAndNums[1], address)
								conn.sendall("invalid amount") 
						else: # action not formatted properly. should be "operation/amount"
							if debug:
								print "Incorrect action sequence. Sending error to client at {0}".format(address)
							conn.sendall("invalid action")
					else: # wrong credentials
						if debug:
							print "Unsuccessful login. Sending error to client at {0}".format(address)
						conn.sendall("login failure")
				else: # user doesn't exist
					if debug:
						print "Invalid username {0}. Sending error to client".format(user) 
					conn.sendall("invalid username")
			else: # if authentication request isn't the first message, we've got a problem
				if debug:
					print "Invalid request. Sending error to client at {0}".format(address)
				conn.sendall("invalid request")
			if debug:
				print "\n"
			conn.close()

def start(): # Init takes user input and begins login service
	userInput = ""
	while userInput not in ["exit","Exit"]:
		userInput = raw_input()
		waitForClient(userInput)

	print("Login Service Exited")

if __name__ == "__main__":
	args = sys.argv

	if "-d" in args:
		debug = True
	else: 
		debug = False
	start()