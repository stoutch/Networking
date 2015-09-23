# Echo server program
import hashlib
import random
import socket
import string
	
users = {"han": "solo", "darth": "vader", "yo": "da"}
accounts = {"han": 0.0, "darth": 0.0, "yo": 0.0}

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
			s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			s.bind((HOST, PORT))
			s.listen(5)
			while 1:
				conn, address = s.accept()
				print "Connected to", address
				data = conn.recv(1024)
				if data == "authentication request":
					challenge = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(64))
					conn.sendall(challenge)
					
					user = conn.recv(1024)
					print "authenticating user", user
					
					if user in users.keys():
						conn.sendall("valid user")
						md5 = hashlib.md5()
						md5.update(user + users[user] + challenge)
						myAuth = md5.hexdigest()
						print "myAuth", myAuth
						theirAuth = conn.recv(1024)
						print "theirAuth", theirAuth
						if myAuth == theirAuth:
							print "Successful login"
							conn.sendall("login success")

							action = conn.recv(1024)
							opAndNums = action.split(":")
							if len(opAndNums) == 2:
								print "correct action sequence"
								operation = opAndNums[0]
								try:
									amount = float(opAndNums[1])
									if operation == "deposit":
										accounts[user] += amount
										conn.sendall(str(accounts[user]))
									elif operation == "withdraw":
										if accounts[user] >= amount:
											accounts[user] -= amount
											conn.sendall(str(accounts[user]))
										else:
											accounts[user] = 0
											conn.sendall("insufficient funds")
									else:
										print "Invalid operation", operation
										conn.sendall("invalid operation")
								except ValueError:
									print "ValueError when trying to parse", opAndNums[1]
									conn.sendall("invalid amount") 
							else:
								print "incorrect action sequence"
								conn.sendall("invalid action")
						else:
							print "Unsuccessful login"
							conn.sendall("login failure")
					else:
						print "Invalid username"
						conn.sendall("invalid username")
				else:
					print "invalid request"
					conn.sendall("invalid request")
				# if not data: break
				# conn.sendall(data)
				conn.close()
server_tcp()