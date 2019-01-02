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
as_prefix4_path = "/data/BGP_LOG/AS-prefix-dataset/IPv4/"
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
as_prefix6_path = "/data/BGP_LOG/AS-prefix-dataset/IPv6/"
for i in os.listdir(as_prefix6_path) :
	with open(as_prefix6_path + i) as f :
		content = f.readlines()
	prefix_list = [x.strip() for x in content]
	print(i + " " + str(prefix_list))
	if(i not in as_prefix6_dict.keys()) :
		as_prefix6_dict[i] = set()
	for j in prefix_list :
		if(':' not in j) : continue
		if('$' in j) : continue
		print(j)
		prefix_real = ipaddress.ip_network(j, strict=False)
		print("**" + str(prefix_real))
                #if(prefix_real.prefixlen > 16) :
                #        prefix_real = prefix_real.supernet(new_prefix=16)
                #else :
		prefix_real = prefix_real.supernet(new_prefix=prefix_real.prefixlen-1)
		as_prefix6_dict[i].add(prefix_real)

write_path = "/data/BGP_LOG/SUSPICIOUS_RAW_DATA/new_result_3.txt"
result = open(write_path, 'w')

ris_data_path = "/data/BGP_LOG/one_hour/one_hour_rrc00.txt"
with open(ris_data_path) as f :
	content = f.readlines()
raw_line_list = [x.strip() for x in content]

raw_cnt = 0
for raw_line in raw_line_list :
	raw_cnt += 1
	print(raw_cnt)
	#print(raw_line)
	cnt = 0
	
	if(raw_line.split('|')[2] != "A"):
		continue
	AS_path = raw_line.split('|')[6].split(' ')
	AS_list = AS_path[len(AS_path)-1]
	AS_list = AS_list.replace("{", "")
	AS_list = AS_list.replace("}", "")
	AS_list = AS_list.split(',')
	raw_prefix_str = raw_line.split('|')[5]
	HJ_type = 1
	for x in AS_list :
		raw_prefix = ipaddress.ip_network(raw_prefix_str)
		if(':' in raw_prefix_str) :
			if(x not in as_prefix6_dict.keys()) :
				data_path = "/data/BGP_LOG/AS-prefix-dataset/IPv6/"
				os.system("whois -h whois.radb.net -- '-i origin AS" + x + "' | grep route6: | awk -F' ' '{print $2}' >> " + data_path + x)
				as_prefix6_dict[x] = set()
				with open(data_path + x) as f :
					content = f.readlines()
				prefix_list = [x.strip() for x in content]
				for j in prefix_list :
					prefix_real = ipaddress.ip_network(j)
					prefix_real = prefix_real.supernet(new_prefix=prefix_real.prefixlen-1)
					as_prefix6_dict[x].add(prefix_real)
			for y in as_prefix6_dict[x] :
				if(is_subnet_of(raw_prefix, y)) :
					HJ_type = 0
					break
		else :
			if(x not in as_prefix4_dict.keys()) :
				data_path = "/data/BGP_LOG/AS-prefix-dataset/IPv4/"
				os.system("whois -h whois.radb.net -- '-i origin AS" + x + "' | grep route: | awk -F' ' '{print $2}' >> " + data_path + x)
				as_prefix4_dict[x] = set()
				with open(data_path + x) as f :
					content = f.readlines()
				prefix_list = [x.strip() for x in content]
				for j in prefix_list :
					prefix_real = ipaddress.ip_network(j)
					if(prefix_real.prefixlen > 16) :
						prefix_real = prefix_real.supernet(new_prefix=16)
					else :
						prefix_real = prefix_real.supernet(new_prefix=prefix_real.prefixlen-1)
					as_prefix4_dict[i].add(prefix_real)
			for y in as_prefix4_dict[x] :
				if(is_subnet_of(raw_prefix, y)) :
					HJ_type = 0
					break

		if(HJ_type == 0) : break
	if(HJ_type == 1) :
		#result.write(raw_line + '\n')
		result.write(raw_line + " type_" + str(HJ_type) + '\n')
		cnt+=1
	else :
		HJ_type = 2
		if(len(AS_list) >= 2) :
			for x in range(0, len(AS_list)-1) :
				asn1 = int(AS_list[x])
				
				for y in range(x+1, len(AS_list)) :
					asn2 = int(AS_list[y])
					if(asn1 > asn2) :
						rel_str = str(asn2) + "-" + str(asn1)
					else :
						rel_str = str(asn1) + "-" + str(asn2)
					if(rel_str in as_rel_set) :
						HJ_type = 0
						break
				if(HJ_type == 0) : break
			if(HJ_type == 2) :
				#result.write(raw_line + '\n')
				result.write(raw_line + " type_" + str(HJ_type) + '\n')
				cnt+=1
		else :
			asn1 = int(AS_list[0])
			asn2 = -1
			for x in range(len(AS_path)-2, -1, -1) :
				if('{' in AS_path[x]) :
					AS_path[x] = AS_path[x].replace("{", "")
					AS_path[x] = AS_path[x].replace("}", "")
					for y in AS_path[x].split(',') :
						if(int(y) != asn1) :
							asn2 = int(y)
							if(asn1 > asn2) :
								rel_str = str(asn2) + "-" + str(asn1)
							else :
								rel_str = str(asn1) + "-" + str(asn2)
							if(rel_str in as_rel_set) :
								HJ_type = 0
								break
					if(HJ_type == 0) :
						break
	
				else :
					if(int(AS_path[x]) != asn1) :
						asn2 = int(AS_path[x])
						if(asn1 > asn2) :
							rel_str = str(asn2) + "-" + str(asn1)
						else :
							rel_str = str(asn1) + "-" + str(asn2)
						if(rel_str in as_rel_set) :
							HJ_type = 0
							break
					if(HJ_type == 0) :
						break
			if(HJ_type == 2) :
				#result.write(raw_line + '\n')
				result.write(raw_line + " type_" + str(HJ_type) + '\n')
				cnt+=1
	if(cnt > 1) :
		print(cnt)
#os.system("sudo rm /data/BGP_LOG/"+date_site+"/"+date_site+ris_site+".txt")
result.close()
