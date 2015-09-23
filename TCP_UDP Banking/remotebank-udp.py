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

		s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		s.settimeout(2) # set timeout to 2 seconds
		s.connect((HOST, PORT))
		s.sendto(user + ':authentication request', (HOST, PORT))
		data, address = s.recvfrom(1024)
		if data != "invalid request" and data != "invalid username":
			if debug:
				print "user", user				
				print "challenge", data	
			challenge = data
			md5 = hashlib.md5()
			md5.update(user + password + challenge)
			auth = md5.hexdigest()
			if debug:
				print "Auth", auth
			action = operation + "/" + amount
			s.sendto(user + ':' + auth + ';' + action, (HOST, PORT))
			result, address = s.recvfrom(1024)
			if result == "invalid message":
				print "Error in body of message"
			elif result == "login failure":
				print "Error authenticating"
			else:
				print "Welcome {0}!".format(user)
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
		elif data == "invalid request":
			print "Invalid request"
		elif data == "invalid username":
			print "Invalid username"
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
	if "test" in args:
		test()
	else:
		start()