import socket
import hashlib
import sys

debug = False

def waitForServer(userInput):
	print "Command:", userInput
	args = userInput.split() # split operators into pieces
	if(args[0] != "remotebank"):
		print("Command invalid")
	else:
		if (len(args) != 6):
			print "Invalid Arguments"
			print "\n"
			return
		connArgs = args[1].split(":")
		if len(connArgs) != 2:
			print "Invalid address arguments"
			print "\n"
			return
		HOST = connArgs[0]
		PORT = int(connArgs[1])
		user = args[2]
		password = args[3]
		operation = args[4]
		amount = args[5]
		try:
			s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # SOCK_STREAM for TCP
			s.connect((HOST, PORT))
			s.sendall('authentication request') # send request for authentication, receive a challenge code
			data = s.recv(1024)
			if data != "invalid request":
				if debug:
					print "user", user
				s.sendall(user) # send the user to the server so they know what to compare the auth token with
				result = s.recv(1024)
				if result == "invalid username":
					print "Invalid username"
				else:
					if debug:
						print "challenge", data	
					# compute the MD5 hash	
					challenge = data
					md5 = hashlib.md5()
					md5.update(user + password + challenge)
					auth = md5.hexdigest()
					if debug:
						print "Auth", auth
					s.sendall(auth)
					result = s.recv(1024)
					if result == "login failure":
						print "Error authenticating"
					elif result == "login success":
						# We got in, so now send the action we want to take on the account. sends as "operation:amount"
						print "Welcome {0}!".format(user)
						action = operation + ":" + amount
						s.sendall(action)
						result = s.recv(1024)
						# various errors. see server code for more detail
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
		except socket.error: # handles errors like when the server isn't running
			print "Could not connect to server. Ensure that it is running"
		print "\n"
		s.close()

def start():
	userInput = ""
	while userInput not in ["exit","Exit"]:
		userInput = raw_input()
		waitForServer(userInput)

	print("Login Service Exited")

def test():
	deposit = "remotebank 127.0.0.1:8591 han solo deposit 10"
	withdraw = "remotebank 127.0.0.1:8591 han solo withdraw 5"
	insufficient_funds = "remotebank 127.0.0.1:8591 han solo withdraw 10"
	invalid_arguments = "remotebank 127.0.0.1:8591 han solo 10"
	invalid_address_arguments = "remotebank 127.0.0.1 han solo deposit 10"
	invalid_user = "remotebank 127.0.0.1:8591 hope solo deposit 10"
	login_failure = "remotebank 127.0.0.1:8591 han solocup deposit 10"
	invalid_amount = "remotebank 127.0.0.1:8591 han solo deposit 10million"
	invalid_operation = "remotebank 127.0.0.1:8591 han solo cup 10"

	waitForServer(deposit)
	waitForServer(withdraw)
	waitForServer(insufficient_funds)
	waitForServer(invalid_arguments)
	waitForServer(invalid_address_arguments)
	waitForServer(invalid_user)
	waitForServer(login_failure)
	waitForServer(invalid_amount)
	waitForServer(invalid_operation)

if __name__ == '__main__':
	args = sys.argv
	
	if "-d" in args:
		debug = True
	else:
		debug = False
	if "test" in args:
		test()
	else:
		start()