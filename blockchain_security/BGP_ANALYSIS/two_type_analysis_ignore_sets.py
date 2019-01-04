#!/usr/bin/env python
import os, sys
from os import listdir
from os.path import isfile, join
import csv
import json
import requests
from datetime import timedelta, date
import time
import operator
from ipaddress import ip_network
import ipaddress


date = sys.argv[1]
#collector = sys.argv[2]
#timestamp = sys.argv[3]


def is_subnet_of(a, b):
	"""
	Returns boolean: is `a` a subnet of `b`?
	"""
	a = ipaddress.ip_network(a)
	b = ipaddress.ip_network(b)
	a_len = a.prefixlen
	b_len = b.prefixlen
	return a_len >= b_len and a.supernet(a_len - b_len) == b


as_rel_file = "./AS_RELATIONSHIP/peer_data/merged_data.txt"
with open(as_rel_file) as f:
	line_list = f.readlines()
line_list = [x.strip() for x in line_list]

as_rel_set = set()

for line in line_list:
   
	asn1 = int(line.split(" ")[0])
	asn2 = int(line.split(" ")[1])
	if(asn1 > asn2) :
		rel_str = str(asn2) + "-" + str(asn1)
	else :
		rel_str = str(asn1) + "-" + str(asn2)
	as_rel_set.add(rel_str)
        






as_prefix4_dict = dict()
as_prefix4_path = "/data/BGP_LOG/AS-prefix-dataset-new/IPv4/"
for i in os.listdir(as_prefix4_path) :
	with open(as_prefix4_path + i) as f :
		content = f.readlines()
	prefix_list = [x.strip() for x in content]
	#print(i + " " + str(prefix_list))
	if(i not in as_prefix4_dict.keys()) :
		as_prefix4_dict[i] = set()
	for j in prefix_list :
		if('.' not in j) : continue
		if(len(j.split(".")) != 4) : continue
		j = j.split(".")[0] + "." + j.split(".")[1] + ".0.0/" + j.split("/")[1] 
		prefix_real = ipaddress.ip_network(j)
		if(prefix_real.prefixlen > 16) :
			prefix_real = prefix_real.supernet(new_prefix=16)
		else :
			prefix_real = prefix_real.supernet(new_prefix=prefix_real.prefixlen-1)
		as_prefix4_dict[i].add(prefix_real)

as_prefix6_dict = dict()
as_prefix6_path = "/data/BGP_LOG/AS-prefix-dataset-new/IPv6/"
for i in os.listdir(as_prefix6_path) :
	with open(as_prefix6_path + i) as f :
		content = f.readlines()
	prefix_list = [x.strip() for x in content]
	#print(i + " " + str(prefix_list))
	if(i not in as_prefix6_dict.keys()) :
		as_prefix6_dict[i] = set()
	for j in prefix_list :
		if(':' not in j) : continue
		if('$' in j) : continue
		#print(j)
		prefix_real = ipaddress.ip_network(j, strict=False)
		#print("**" + str(prefix_real))
                #if(prefix_real.prefixlen > 16) :
                #        prefix_real = prefix_real.supernet(new_prefix=16)
                #else :
		prefix_real = prefix_real.supernet(new_prefix=prefix_real.prefixlen-1)
		as_prefix6_dict[i].add(prefix_real)

write_path = "/data/BGP_LOG/hijacking_include_BTC/two_type_analysis/" + date + "/" + "20181022ALL1800_setIgnore_type4_ipxAdd_again"
result = open(write_path, 'w')

ris_data_path = "/data/BGP_LOG/hijacking_include_BTC/" + date + "/" + "20181022ALL1800"
with open(ris_data_path) as f :
	content = f.readlines()
raw_line_list = [x.strip() for x in content]

raw_cnt = 0
print("analysis start!")

not_type_0_set = set()
for raw_line in raw_line_list :
	if(',' in raw_line) : continue
	raw_cnt += 1
	print(raw_cnt)
	print(raw_line)
	cnt = 0
	
	if(raw_line.split('|')[2] != "A"):
		continue
	AS_path_str = raw_line.split('|')[6]
	AS_path_str = AS_path_str.replace("{", "")
	AS_path_str = AS_path_str.replace("}", "")
	AS_path = AS_path_str.split(' ')
	
	lastASset = set()
	lastAS = []
	lastAS.append(AS_path[len(AS_path)-1])
	lastASset.add(lastAS[len(lastAS)-1])
	for x in range(len(AS_path)-2, -1, -1) :
		if(AS_path[x] not in lastASset) :
			lastAS.append(AS_path[x])
			lastASset.add(AS_path[x])
		if(len(lastAS) == 4) : break

	raw_prefix_str = raw_line.split('|')[5]
	HJ_type = 1
	print(lastAS)
	if(lastAS[0]+raw_prefix_str not in not_type_0_set) :
		raw_prefix = ipaddress.ip_network(raw_prefix_str)
		if(':' in raw_prefix_str) :
			if(lastAS[0] not in as_prefix6_dict.keys()) :
				data_path = "/data/BGP_LOG/AS-prefix-dataset/IPv6/"
				os.system("whois -h whois.radb.net -- '-i origin AS" + lastAS[0] + "' | grep route6: | awk -F' ' '{print $2}' >> " + data_path + lastAS[0])
				as_prefix6_dict[lastAS[0]] = set()
				with open(data_path + lastAS[0]) as f :
					content = f.readlines()
				prefix_list = [x.strip() for x in content]
				for j in prefix_list :
					prefix_real = ipaddress.ip_network(j)
					prefix_real = prefix_real.supernet(new_prefix=prefix_real.prefixlen-1)
					as_prefix6_dict[lastAS[0]].add(prefix_real)
			if(lastAS[0] not in as_prefix6_dict.keys()) : continue
			for y in as_prefix6_dict[lastAS[0]] :
				if(is_subnet_of(raw_prefix, y)) :
					not_type_0_set.add(lastAS[0]+raw_prefix_str)
					HJ_type = 0
					break
		else :
			if(lastAS[0] not in as_prefix4_dict.keys()) :
				data_path = "/data/BGP_LOG/AS-prefix-dataset/IPv4/"
				os.system("whois -h whois.radb.net -- '-i origin AS" + lastAS[0] + "' | grep route: | awk -F' ' '{print $2}' >> " + data_path + lastAS[0])
				as_prefix4_dict[lastAS[0]] = set()
				with open(data_path + lastAS[0]) as f :
					content = f.readlines()
				prefix_list = [x.strip() for x in content]
				for j in prefix_list :
					prefix_real = ipaddress.ip_network(j)
					if(prefix_real.prefixlen > 16) :
						prefix_real = prefix_real.supernet(new_prefix=16)
					else :
						prefix_real = prefix_real.supernet(new_prefix=prefix_real.prefixlen-1)
					as_prefix4_dict[i].add(prefix_real)
			if(lastAS[0] not in as_prefix4_dict.keys()) : continue
			for y in as_prefix4_dict[lastAS[0]] :
				if(is_subnet_of(raw_prefix, y)) :
					not_type_0_set.add(lastAS[0]+raw_prefix_str)
					HJ_type = 0
					break

		if(HJ_type == 1) :
			#result.write(raw_line + '\n')
			HJ_type = 0
			result.write(raw_line + " type_" + str(HJ_type) + '\n')
			cnt+=1
			continue

	if(len(lastAS)<2) : continue
	asn1 = int(lastAS[0])
	asn2 = int(lastAS[1])
	if(asn1 > asn2) :
		rel_str = str(asn2) + "-" + str(asn1)
	else :
		rel_str = str(asn1) + "-" + str(asn2)
	if(rel_str not in as_rel_set) :
		HJ_type = 1
		result.write(raw_line + " type_" + str(HJ_type) + '\n')
		cnt+=1
		continue
	if(len(lastAS)<3) : continue
	asn1 = int(lastAS[1])
	asn2 = int(lastAS[2])	
	if(asn1 > asn2) :
		rel_str = str(asn2) + "-" + str(asn1)
	else :
		rel_str = str(asn1) + "-" + str(asn2)
	if(rel_str not in as_rel_set) :
		HJ_type = 2
		result.write(raw_line + " type_" + str(HJ_type) + '\n')
		cnt+=1
		continue
	if(len(lastAS)<4) : continue
	asn1 = int(lastAS[2])
	asn2 = int(lastAS[3])	
	if(asn1 > asn2) :
		rel_str = str(asn2) + "-" + str(asn1)
	else :
		rel_str = str(asn1) + "-" + str(asn2)
	if(rel_str not in as_rel_set) :
		HJ_type = 3
		result.write(raw_line + " type_" + str(HJ_type) + '\n')
		cnt+=1
		continue

	if(cnt >= 2) :
		sys.exit()
#os.system("sudo rm /data/BGP_LOG/"+date_site+"/"+date_site+ris_site+".txt")
result.close()
