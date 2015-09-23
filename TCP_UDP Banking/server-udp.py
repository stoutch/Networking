# Echo server program
import hashlib
import random
import socket
import string
	
users = {"han": "solo", "darth": "vader", "yo": "da"}
accounts = {"han": 0.0, "darth": 0.0, "yo": 0.0}
challenges = {}


class server_tcp:
	def __init__(self): # Init takes user input and begins login service
		userInput = ""
		while userInput not in ["exit","Exit"]:
			userInput = raw_input()
			self.waitForClient(userInput)

		print("Login Service Exited")

	def waitForClient(self, userInput):
		args = userInput.split() # split operators into pieces	
		if(args[0] != "bank-server"):
			print("Command invalid")
		else:
			HOST = ''
			PORT = int(args[1])
			s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
			s.bind((HOST, PORT))
			while 1:
				data, address = s.recvfrom(1024)
				user = data.split(":")[0]
				print "User", user
				if not (user in users): 
					s.sendto("invalid username", address)
				else:
					message = data.split(":")[1]
					print "message", message
					key = user + address[0]
					print "Connected to", address

					if message == "authentication request":
						challenge = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(64))
						s.sendto(challenge, address)
						challenges[key] = challenge

					elif key in challenges:

						print "authenticating user", user
						body = message.split(";")
						if len(body) == 2:					
							md5 = hashlib.md5()
							md5.update(user + users[user] + challenges[key])
							myAuth = md5.hexdigest()
							theirAuth = body[0]
							print "myAuth", myAuth
							print "theirAuth", theirAuth

							if myAuth == theirAuth:
								print "Successful login"
								print "{0} logged in".format(user)
								# s.sendto("login success", address)	
								action = body[1]
								opAndNums = action.split("/")
								if len(opAndNums) == 2:
									print "correct action sequence"
									operation = opAndNums[0]
									try:
										amount = float(opAndNums[1])
										if operation == "deposit":
											accounts[user] += amount
											s.sendto(str(accounts[user]), address)
										elif operation == "withdraw":
											if accounts[user] >= amount:
												accounts[user] -= amount
												s.sendto(str(accounts[user]), address)
											else:
												accounts[user] = 0
												s.sendto("insufficient funds", address)
										else:
											print "Invalid operation", operation
											s.sendto("invalid operation", address)
									except ValueError:
										print "ValueError when trying to parse", opAndNums[1]
										s.sendto("invalid amount", address) 
								else:
									print "incorrect action sequence"
									s.sendto("invalid action", address)
							else:
								print "Unsuccessful login"
								s.sendto("login failure", address)
						else:
							print "incorrect body"
							s.sendto("invalid message", address)

						del challenges[key]
						
					else:
						print "invalid request"
						s.sendto("invalid request", address)
				# if not data: break
				# s.sendto(data)
			s.close()
server_tcp()