#!/usr/bin/env python

import sys
import csv
import ipaddress
import os.path
import random
import hashlib
from array import *
from collections import defaultdict

def prep_ip_address(filename):
    with open(filename) as f:
        line_list = f.readlines()
    line_list = [x.strip() for x in line_list]

    as_ip_address = []
    for line in line_list:
        host = ipaddress.ip_interface(line.split()[0])
        as_ip_address.append(host)
    return as_ip_address

def prep_bitcoin_full_node_ip_address(filename):
    with open(filename) as f:
        line_list = f.readlines()
    line_list = [x.strip() for x in line_list]

    as_ip_address = []
    for line in line_list:
        ip = ipaddress.ip_address(line.split()[0])
        as_ip_address.append(ip)
    return as_ip_address

def prep_decoy_as(filename):
    with open(filename) as f:
        line_list = f.readlines()
    line_list = [x.strip() for x in line_list]

    as_list = []
    for line in line_list:
        asn = int(line.split()[0])
        as_list.append(asn)
    return as_list
def prep_malicious_as(filename):
    with open(filename) as f:
        line_list = f.readlines()
    line_list = [x.strip() for x in line_list]
    line = line_list[0]
    malicious_as = [int(x) for x in line.split()]
    return malicious_as

sk = 8526032614150639691813360186279248162419447383089891172061451875764310536150 #random.getrandbits(256)

ADDRMAN_TRIED_BUCKETS_PER_GROUP = 8
ADDRMAN_TRIED_BUCKET_COUNT = 256
ADDRMAN_NEW_BUCKETS_PER_SOURCE_GROUP = 64
ADDRMAN_NEW_BUCKET_COUNT = 1024
ADDRMAN_BUCKET_SIZE = 64

def get_tried_bucket(sk, ip):
    ip_as_bytes = bytes(map(int, ip.split('.')))
    m1 = hashlib.sha256()
    m1.update(str(sk).encode())
    m1.update(ip_as_bytes)
    hash1 = int.from_bytes(m1.digest()[:8],byteorder='big')
    m2 = hashlib.sha256()
    m2.update(str(sk).encode())
    m2.update(ip_as_bytes[:2])
    m2.update(str(hash1 % ADDRMAN_TRIED_BUCKETS_PER_GROUP).encode())
    hash2 = int.from_bytes(m2.digest()[:8],byteorder='big')
    return hash2 % ADDRMAN_TRIED_BUCKET_COUNT

def get_new_bucket(sk, src_ip, ip):
    ip_as_bytes = bytes(map(int, ip.split('.')))
    src_ip_as_bytes = bytes(map(int, src_ip.split('.')))
    m1 = hashlib.sha256()
    m1.update(str(sk).encode())
    m1.update(ip_as_bytes[:2])
    m1.update(src_ip_as_bytes[:2])
    hash1 = int.from_bytes(m1.digest()[:8],byteorder='big')
    m2 = hashlib.sha256()
    m2.update(str(sk).encode())
    m2.update(src_ip_as_bytes[:2])
    m2.update(str(hash1 % ADDRMAN_NEW_BUCKETS_PER_SOURCE_GROUP).encode())
    hash2 = int.from_bytes(m2.digest()[:8],byteorder='big')
    return hash2 % ADDRMAN_NEW_BUCKET_COUNT

def get_bucket_position(sk, fNew, nBucket, ip):
    ip_as_bytes = bytes(map(int, ip.split('.')))
    m = hashlib.sha256()
    m.update(str(sk).encode())
    if fNew:
        m.update('N'.encode())
    else:
        m.update('K'.encode())
    m.update(str(nBucket).encode())
    m.update(ip_as_bytes)
    h = int.from_bytes(m.digest()[:8],byteorder='big')  
    return h % ADDRMAN_BUCKET_SIZE

# print(get_new_bucket(sk, src_ip, ip), get_bucket_position(sk, True, get_new_bucket(sk, src_ip, ip), ip))
# print(get_tried_bucket(sk, ip), get_bucket_position(sk, False, get_tried_bucket(sk, ip), ip)) 


def get_random_ip(networks):
    selected_network = random.sample(networks, 1)[0]
    index = random.randint(0,selected_network.num_addresses-1)
    return str(selected_network[index])



victimAS = 24940
attackerAS = 3356

attacker_ip_range_file = "./config/asn-to-ip/"+str(attackerAS)+".txt"
attacker_hosts = prep_ip_address(attacker_ip_range_file)
#print(attacker_hosts)
decoy_hosts = []
decoy_as_file = "./decoy-as/"+str(victimAS)+"/"+str(victimAS)+"-"+str(attackerAS)+".txt"
decoy_as_list = prep_decoy_as(decoy_as_file)
for q in range (100) :
	for asn in decoy_as_list:
	    ip_range_file = "./config/asn-to-ip/"+str(asn)+".txt"
	    if not os.path.isfile(ip_range_file):
	        continue #just ignore for now
	    hosts = prep_ip_address(ip_range_file)
	    decoy_hosts += hosts

	decoy_16_network = []
	for host in decoy_hosts:
	    if host.network.prefixlen < 16:
	        for network in list(host.network.subnets(new_prefix=16)):
	            decoy_16_network += [network]
	    else:
	        decoy_16_network += [host.network]



	src_ip = get_random_ip(decoy_16_network) # choose a random attacker ip address
	out = open("./attack_resource/"+ str(src_ip) +".txt", "w")
	print(src_ip)
	print("*****")

	#choose 1000 random decoy IP address
	selected_decoy_ips = []
	for i in range(1000):
	    decoy_ip = get_random_ip(decoy_16_network)
	    # while decoy_ip in inserted_decoy_ips:
	    #     decoy_ip = get_random_ip(decoy_16_network)
	    selected_decoy_ips += [decoy_ip]
	    out.write(str(decoy_ip) + '\n')
	    print(str(decoy_ip) + '\n')
	print(src_ip)
	print("*****")
	print(len(selected_decoy_ips))

	out.close()
# print(selected_decoy_ips)

# times = 20
# out = open("./temp-10000/"+sys.argv[1]+".txt", "w+")

# while (times > 0):
#     times -= 1
#     new = [["-1" for x in range(ADDRMAN_BUCKET_SIZE)] for y in range(ADDRMAN_NEW_BUCKET_COUNT)] 


#     occupy = 10000
#     for i in range(occupy):
#         new_bucket = random.randint(0, ADDRMAN_NEW_BUCKET_COUNT-1)
#         new_bucket_slot = random.randint(0, ADDRMAN_BUCKET_SIZE-1)
#         new[new_bucket][new_bucket_slot] = "0"

#     rounds = int(sys.argv[1]) #expected number ADDR messages to be sent

#     inserted_decoy_ips = []

#     while rounds > 0:
#         rounds -= 1
#         src_ip = get_random_ip(decoy_16_network) # choose a random attacker ip address

#         #choose 1000 random decoy IP address
#         selected_decoy_ips = []
#         for i in range(1000):
#             decoy_ip = get_random_ip(decoy_16_network)
#             # while decoy_ip in inserted_decoy_ips:
#             #     decoy_ip = get_random_ip(decoy_16_network)
#             selected_decoy_ips += [decoy_ip]
#         # print(selected_decoy_ips)

#         for ip in selected_decoy_ips:
#             new_bucket = get_new_bucket(sk, src_ip, ip)
#             new_bucket_slot = get_bucket_position(sk, True, new_bucket, ip)
#             if new[new_bucket][new_bucket_slot] == "-1":
#                 if ip in inserted_decoy_ips:
#                     continue
#                 new[new_bucket][new_bucket_slot] = ip
#                 inserted_decoy_ips += [ip]

#     filled_slot = 0

#     for i in range(ADDRMAN_NEW_BUCKET_COUNT):
#         for j in range(ADDRMAN_BUCKET_SIZE):
#             if new[i][j] != "-1" and new[i][j] != "0":
#                 filled_slot += 1
#         # print(new[i])
    
#     out.write(str(filled_slot) + "\n")
