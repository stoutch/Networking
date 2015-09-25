# Echo server program
import hashlib
import random
import socket
import string
import sys
	
users = {"han": "solo", "darth": "vader", "yo": "da"}
accounts = {"han": 0.0, "darth": 0.0, "yo": 0.0}
challenges = {}
debug = False

def waitForClient(userInput):
	args = userInput.split() # split input
	if(args[0] != "bank-server"): # make sure we have right command
		print("Command invalid")
	else:
		HOST = '' # accept all sources
		PORT = int(args[1]) 
		s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # SOCK_DGRAM for UDP
		s.bind((HOST, PORT))
		while 1:
			data, address = s.recvfrom(1024)
			user = data.split(":")[0] # get data from client
			if debug:
				print "User", user
			if not (user in users): # if the user sent is not in the dict, no need continuing
				if debug:
					print "Invalid username {0}. Sending error to client".format(user) 
				s.sendto("invalid username", address)
			else:
				message = data.split(":")[1]
				key = user + address[0] + str(address[1]) # use this to identify a "connection"
				if debug:
					print "message", message
					print "Connected to", address

				if message == "authentication request": # this should be the first data sent over'
					# generate random challenge, send that to the client. from http://stackoverflow.com/questions/2257441/random-string-generation-with-upper-case-letters-and-digits-in-python
					challenge = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(64)) 
					if debug:
						print "Sending challenge to client at {0}".format(address) 
					s.sendto(challenge, address)
					challenges[key] = challenge # store the challenge for comparison later

				elif key in challenges: # if the key exists, then we know they've already asked for authentication and are now sending data
					# we do two things at this step, authenticate the user. If that succeeds then process the data they've sent
					if debug:
						print "authenticating user", user
					body = message.split(";")
					if len(body) == 2:
						# validate the MD5 hash				
						md5 = hashlib.md5()
						md5.update(user + users[user] + challenges[key])
						myAuth = md5.hexdigest()
						theirAuth = body[0] # body comes in as auth;operation/amount
						if debug:
							print "myAuth", myAuth
							print "theirAuth", theirAuth

						if myAuth == theirAuth:
							if debug:
								print "{0} logged in".format(user)
							action = body[1] # get the operation/action section
							opAndNums = action.split("/")
							if len(opAndNums) == 2: # validate the operation/action section
								if debug:
									print "correct action sequence"
								operation = opAndNums[0]
								try: # bunch of validations here on what is sent over. if good data, do the operation
									amount = float(opAndNums[1])
									if operation == "deposit":
										accounts[user] += amount
										if debug:
											print "Deposited money. Sending new balance to client at {0}".format(address)
										s.sendto(str(accounts[user]), address)
									elif operation == "withdraw":
										if accounts[user] >= amount: # check for insufficient funds
											accounts[user] -= amount
											if debug:
												print "Withdrew money. Sending new balance to client at {0}".format(address)
											s.sendto(str(accounts[user]), address)
										else:
											accounts[user] = 0
											if debug:
												print "Insufficient funds. Sending balance of $0.00 to client at {0}".format(address)
											s.sendto("insufficient funds", address)
									else: #not valid operation
										if debug:
											print "Invalid operation {0}. Sending error to client at {1}".format(operation, address)
										s.sendto("invalid operation", address)
								except ValueError:
									if debug:
										print "ValueError when trying to parse {0}. Sending error to client at {1}".format(opAndNums[1], address)
									s.sendto("invalid amount", address) 
							else: # action part of data wasn't formatted right
								if debug:
									print "Incorrect action sequence. Sending error to client at {0}".format(address)
								s.sendto("invalid action", address)
						else: # couldn't validate user
							if debug:
								print "Unsuccessful login. Sending error to client at {0}".format(address)
							s.sendto("login failure", address)
					else:  # body not formatted right
						if debug:
							print "Incorrect body. Sending error to client at {0}".format(address)
						s.sendto("invalid message", address)

					del challenges[key] # once we've validated (or attempted to validate) this user, delete the challenge
					
				else: # if this is reached it basically means the client is out of sync with the server
					if debug:
						print "Invalid request. Sending error to client at {0}".format(address)
					s.sendto("invalid request", address)
			if debug:
				print "\n"
		s.close()

def start():
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