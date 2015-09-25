import socket
import hashlib
import sys

debug = False

def waitForServer(userInput, timeouts):
	print "Command:", userInput
	args = userInput.split() # split operators into pieces
	if(args[0] != "remotebank"):
		print("Command invalid")
	else:
		if (len(args) != 6): # make sure we have correct number of args
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
			s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
			s.settimeout(3) # set timeout to 3 seconds
			s.connect((HOST, PORT))
			s.sendto(user + ':authentication request', (HOST, PORT)) # send authentication request. We receive challenge from this
			data, address = s.recvfrom(1024)
			if data != "invalid request" and data != "invalid username": # make sure no errors
				if debug:
					print "user", user				
					print "challenge", data	
				challenge = data # compute MD5
				md5 = hashlib.md5()
				md5.update(user + password + challenge)
				auth = md5.hexdigest()
				if debug:
					print "Auth", auth
				action = operation + "/" + amount # format the action to take on account
				s.sendto(user + ':' + auth + ';' + action, (HOST, PORT)) # add auth code and action together with user and send
				result, address = s.recvfrom(1024) # result of that action. either error message or confirmation of deposit/withdrawl
				# lots of various errors. For a better understanding, check out the server code
				if result == "invalid message":
					print "Error in body of message"
				elif result == "login failure":
					print "Error authenticating"
				else: # we got in!
					print "Welcome {0}!".format(user)
					if result == "invalid action":
						print "Invalid action on account"
					elif result == "invalid amount":
						print "Value error: amount given is not a number"
					elif result == "invalid operation":
						print "Invalid banking operation"
					elif result == "insufficient funds":
						print "Insufficient funds. Withdrew remaining funds from account. Balance is $0.00"
					else: # no errors, so this data must be the new account balance
						if operation == "deposit":
							print "Successfully deposited ${0} into account. Balance is now ${1}".format(amount, result)
						else:
							print "Successfully withdrew ${0} from account. Balance is now ${1}".format(amount, result)
			elif data == "invalid request":
				print "Invalid request"
			elif data == "invalid username":
				print "Invalid username"
			timeouts = 0
		except socket.timeout: # check for timeouts. max of 4 timeouts before calling it quits
			if timeouts >= 4:
				print "4 consecutive timeouts. Server is unresponsive. Exiting."
			else:
				if debug:
					print "Timeout. Retrying"
				timeouts += 1
				waitForServer(userInput, timeouts)		
		except socket.error as e: # handles errors like when the server isn't running
			print "Could not connect to server. Ensure that it is running"

		print "\n"
		s.close()

def start():
	userInput = ""
	while userInput not in ["exit","Exit"]:
		userInput = raw_input()
		waitForServer(userInput, 0)

	print("Login Service Exited")

def test(): # testing stuff
	deposit = "remotebank 127.0.0.1:8591 han solo deposit 10"
	withdraw = "remotebank 127.0.0.1:8591 han solo withdraw 5"
	insufficient_funds = "remotebank 127.0.0.1:8591 han solo withdraw 10"
	invalid_arguments = "remotebank 127.0.0.1:8591 han solo 10"
	invalid_address_arguments = "remotebank 127.0.0.1 han solo deposit 10"
	invalid_user = "remotebank 127.0.0.1:8591 hope solo deposit 10"
	login_failure = "remotebank 127.0.0.1:8591 han solocup deposit 10"
	invalid_amount = "remotebank 127.0.0.1:8591 han solo deposit 10million"
	invalid_operation = "remotebank 127.0.0.1:8591 han solo cup 10"

	waitForServer(deposit, 0)
	waitForServer(withdraw, 0)
	waitForServer(insufficient_funds, 0)
	waitForServer(invalid_arguments, 0)
	waitForServer(invalid_address_arguments, 0)
	waitForServer(invalid_user, 0)
	waitForServer(login_failure, 0)
	waitForServer(invalid_amount, 0)
	waitForServer(invalid_operation, 0)

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