import struct
import socket
import time
import hashlib
import binascii
import random

#####
magic = "f9beb4d9"

def makeMessage(magic,command,payload):
    checksum = hashlib.sha256(hashlib.sha256(payload).digest()).digest()[0:4]
    return magic.decode("hex")+struct.pack('12sI4s',command,len(payload),checksum)+payload
def makeVersionPayload():
    version = 70002
    services = 0
    timestamp = int(time.time())

    addr_you = "10.0.0.1"
    services_you = 0
    port_you = 8333

    addr_me = "10.0.0.2"
    services_me = 0
    port_me = 8333	

    nonce = 0

    user_agent_bytes = 0
    start_height = 0
    relay = 1

    #https://bitcoin.org/en/developer-reference#version
    payload = "";
    payload += struct.pack("i",version)
    payload += struct.pack("Q",services)
    payload += struct.pack("q",timestamp)
    payload += struct.pack("Q",services_you)
    payload += struct.pack(">16s",addr_you)
    payload += struct.pack(">H",port_you)
    payload += struct.pack("Q",services_me)
    payload += struct.pack(">16s",addr_me)
    payload += struct.pack(">H",port_me)
    payload += struct.pack("Q",nonce)
    payload += struct.pack("B",user_agent_bytes)
    payload += struct.pack("i",start_height)
    payload += struct.pack("B",relay)
    return payload

def convertToHex(ipv4):
    ipv4_list = ipv4.split('.')
    result = ''
    for x in ipv4_list :
	
	x = int(x)
	first = x/16
	if first == 10 :
		result += 'a'
	elif first == 11 :
		result += 'b'
	elif first == 12 :
		result += 'c'
	elif first == 13 :
		result += 'd'
	elif first == 14 :
		result += 'e'
	elif first == 15 :
		result += 'f'
	else :
		result += str(first)
	second = x%16
	if second == 10 :
		result += 'a'
	elif second == 11 :
		result += 'b'
	elif second == 12 :
		result += 'c'
	elif second == 13 :
		result += 'd'
	elif second == 14 :
		result += 'e'
	elif second == 15 :
		result += 'f'
	else :	
		result += str(second)
    return result

ip = socket.gethostbyname("10.0.0.1")
port = 8333
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

#
#sock.settimeout(50)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_LINGER, struct.pack('ii', 1, 0))
#


sock.bind(('10.0.0.2',1235))
print "connected to node..."
sock.connect((ip,port))

msg = makeMessage(magic,"version",makeVersionPayload())
print "sending version packet"
sock.send(msg)
time.sleep(2)
msg2 = makeMessage(magic,"verack","")
sock.send(msg2)
#sock.settimeout(2.0)
"""
while 1:
    msg = sock.recv(2**10)
    if not msg:
        print "done"
    else:
        print msg.encode("hex")
"""    

############ADDR SENDING############

count = 1
timestamp = int(time.time())
services = 1


ip_addr = '75.70.234.54' # this ip_addr will be inserted into NEW table. 


stringIPaddr = '00000000000000000000ffff' + convertToHex(ip_addr)
targetIP = stringIPaddr.decode("hex")


port = 1235
payload = ""
payload += struct.pack("b", count)
payload += struct.pack("I", timestamp)
payload += struct.pack("Q", services)
payload += struct.pack(">16s", targetIP)
payload += struct.pack(">H", port)



msg3 = makeMessage(magic,"addr",payload)
print msg
sock.send(msg3)

sock.recv(1024)

print "ADDR SENDING..."
time.sleep(5)

exit()


##############



"""
    print "*"
    msg = sock.recv(2**20)
    print msg.encode("hex")
    #print msg.encode("hex")
    print "done"
    exit()
"""

