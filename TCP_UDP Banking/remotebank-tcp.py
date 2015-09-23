import socket
import hashlib

# HOST = ''    # The remote host
# PORT = 50007              # The same port as used by the server
# s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# s.connect((HOST, PORT))
# s.sendall('authentication request')
# data = s.recv(1024)
# s.close()
# print 'Received', repr(data)

class client_tcp:
	def __init__(self): # Init takes user input and begins login service
		userInput = ""
		while userInput not in ["exit","Exit"]:
			userInput = raw_input()
			self.waitForServer(userInput)

		print("Login Service Exited")

	def waitForServer(self, userInput):
		args = userInput.split() # split operators into pieces
		if(args[0] != "remotebank"):
			print("Command invalid")
		else:
			if (len(args) != 6):
				print "Invalid Arguments"
				return
			connArgs = args[1].split(":")
			HOST = connArgs[0]
			PORT = int(connArgs[1])
			user = args[2]
			password = args[3]
			operation = args[4]
			amount = args[5]

			s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			s.connect((HOST, PORT))
			s.sendall('authentication request')
			data = s.recv(1024)
			if data != "invalid request":
				print "user", user
				s.sendall(user)
				result = s.recv(1024)
				if result == "invalid username":
					print "Invalid username"
				else:
					print "challenge", data		
					challenge = data
					md5 = hashlib.md5()
					md5.update(user + password + challenge)
					auth = md5.hexdigest()
					print "Auth", auth
					s.sendall(auth)
					result = s.recv(1024)
					if result == "login failure":
						print "Error authenticating"
					elif result == "login success":
						print "Welcome", user
						action = operation + ":" + amount
						s.sendall(action)
						result = s.recv(1024)
						if result == "invalid action":
							print "Invalid action on account"
						elif result == "invalid amount":
							print "Value error: amount given is not a number"
						elif result == "invalid operation":
							print "Invalid banking operation"
						elif result == "insufficient funds":
							print "Insufficient funds. Withdrew remaining funds from account. Balance is $0.00"
						else:
							if operation == "deposit":
								print "Successfully deposited ${0} into account. Balance is now ${1}".format(amount, result)
							else:
								print "Successfully withdrew ${0} from account. Balance is now ${1}".format(amount, result)
			else:
				print "Invalid request"

			s.close()

client_tcp()