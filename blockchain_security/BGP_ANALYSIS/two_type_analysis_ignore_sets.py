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

def ipv4_ownership_check(prefix, asn) :
	for y in as_prefix4_dict[asn] :
		if(is_subnet_of(prefix, y)) :
			return True
	return False
def ipv6_ownership_check(prefix, asn) :
	for y in as_prefix6_dict[asn] :
		if(is_subnet_of(prefix, y)) :
			return True
	return False

as_rel_file = "/data/BGP_LOG/AS_RELATIONSHIP_DATA/peer_data/peering-data-superset"
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
as_prefix6_dict = dict()

all_asn_path = "/data/BGP_LOG/all-asn"
with open(all_asn_path) as f :
	content = f.readlines()
#print(content)
asn_list = [x.strip() for x in content]
for i in asn_list :
	as_prefix4_dict[i] = set()
	as_prefix6_dict[i] = set()

as_prefix_ipv4_dataset_path = "/data/BGP_LOG/AS-prefix-dataset/prefix-superset/prefix_ipv4_superset"
with open(as_prefix_ipv4_dataset_path) as f :
	content = f.readlines()
as_prefix_ipv4_list = [x.strip() for x in content]
for i in as_prefix_ipv4_list :
	asn = i.split(',')[0]
	prefix_str = i.split(',')[1]
	prefix_str = prefix_str.split(".")[0] + "." + prefix_str.split(".")[1] + ".0.0/" + prefix_str.split("/")[1]
	prefix_real = ipaddress.ip_network(prefix_str)
	if(prefix_real.prefixlen > 16) :
		prefix_real = prefix_real.supernet(new_prefix=16)
	else :
		prefix_real = prefix_real.supernet(new_prefix=prefix_real.prefixlen-1)
	as_prefix4_dict[asn].add(prefix_real)

as_prefix_ipv6_dataset_path = "/data/BGP_LOG/AS-prefix-dataset/prefix-superset/prefix_ipv6_superset"
with open(as_prefix_ipv6_dataset_path) as f :
	content = f.readlines()
as_prefix_ipv6_list = [x.strip() for x in content]
for i in as_prefix_ipv6_list :
	asn = i.split(',')[0]
	prefix_str = i.split(',')[1]
	prefix_real = ipaddress.ip_network(prefix_str, strict=False)
	prefix_real = prefix_real.supernet(new_prefix=prefix_real.prefixlen-2)
	as_prefix6_dict[asn].add(prefix_real)
"""
radb_data_path = "/data/BGP_LOG/AS-prefix-dataset/prefix-radb/"
for i in os.listdir(radb_data_path) : # i is string
	as_prefix4_dict[i] = set()
	as_prefix6_dict[i] = set()

	with open(radb_data_path + i) as f :
		content = f.readlines()
	prefix_list = [x.strip() for x in content]

	#print(i + " " + str(prefix_list))
	for j in prefix_list :
		if(':' in j) :
			if("route" in j) : continue
			prefix_real = ipaddress.ip_network(j, strict=False)
			prefix_real = prefix_real.supernet(new_prefix=prefix_real.prefixlen-2)
			as_prefix6_dict[i].add(prefix_real)
		elif('.' in j) :
			j = j.split(".")[0] + "." + j.split(".")[1] + ".0.0/" + j.split("/")[1] 
			prefix_real = ipaddress.ip_network(j)
			if(prefix_real.prefixlen > 16) :
				prefix_real = prefix_real.supernet(new_prefix=16)
			else :
				prefix_real = prefix_real.supernet(new_prefix=prefix_real.prefixlen-1)
			as_prefix4_dict[i].add(prefix_real)

ripe_stat_dat_path = "/data/BGP_LOG/AS-prefix-dataset/prefix-ripe-stat"
with open(ripe_stat_dat_path) as f :
	content = f.readlines()
prefix_list = [x.strip() for x in content]
for j in prefix_list :
	asn = j.split(' ')[0]
	if(asn not in as_prefix4_dict.keys()) : continue
	prefix_str = j.split(' ')[1]
	if(':' in prefix_str) :
		prefix_real = ipaddress.ip_network(prefix_str, strict=False)
		prefix_real = prefix_real.supernet(new_prefix=prefix_real.prefixlen-2)
		as_prefix6_dict[i].add(prefix_real)
	elif('.' in j) :		
		prefix_str = prefix_str.split(".")[0] + "." + prefix_str.split(".")[1] + ".0.0/" + prefix_str.split("/")[1] 
		prefix_real = ipaddress.ip_network(prefix_str)
		if(prefix_real.prefixlen > 16) :
			prefix_real = prefix_real.supernet(new_prefix=16)
		else :
			prefix_real = prefix_real.supernet(new_prefix=prefix_real.prefixlen-1)
		as_prefix4_dict[i].add(prefix_real)

ipv4_routeviews_plus_ipinfo_path = "/data/BGP_LOG/AS-prefix-dataset/routeviews_plus_ipinfo_IPv4/"

for i in os.listdir(ipv4_routeviews_plus_ipinfo_path) : # i is string
	if(i not in as_prefix4_dict.keys()) : continue
	with open(ipv4_routeviews_plus_ipinfo_path + i) as f :
		content = f.readlines()
	prefix_list = [x.strip() for x in content]

	for j in prefix_list :
		if('.' not in j) : continue
		j = j.split(".")[0] + "." + j.split(".")[1] + ".0.0/" + j.split("/")[1] 
		prefix_real = ipaddress.ip_network(j)
		if(prefix_real.prefixlen > 16) :
			prefix_real = prefix_real.supernet(new_prefix=16)
		else :
			prefix_real = prefix_real.supernet(new_prefix=prefix_real.prefixlen-1)
		as_prefix4_dict[i].add(prefix_real)

ipv6_routeviews_plus_ipinfo_path = "/data/BGP_LOG/AS-prefix-dataset/routeviews_plus_ipinfo_IPv6/"
for i in os.listdir(ipv6_routeviews_plus_ipinfo_path) : # i is string
	if(i not in as_prefix4_dict.keys()) : continue
	with open(ipv6_routeviews_plus_ipinfo_path + i) as f :
		content = f.readlines()
	prefix_list = [x.strip() for x in content]

	for j in prefix_list :
		prefix_real = ipaddress.ip_network(j, strict=False)
		
		prefix_real = prefix_real.supernet(new_prefix=prefix_real.prefixlen-2)

		as_prefix6_dict[i].add(prefix_real)
"""
#############ABOVE : DATA IMPORTIMG##################


write_path = "/data/BGP_LOG/hijacking_include_BTC/two_type_analysis/" + date + "/" + date + "_sevenhour0000_4type_result_supersetTest"
result = open(write_path, 'w')

#ris_data_path = "/data/BGP_LOG/hijacking_include_BTC/" + date + "/" + "20181022ALL1800"
ris_data_path = "/data/BGP_LOG/hijacking_include_BTC/20181022/20181022ALL0007"
with open(ris_data_path) as f :
	content = f.readlines()
raw_line_list = [x.strip() for x in content]

raw_cnt = 0
print("analysis start!")

not_type_0_set = set()
for raw_line in raw_line_list :
	
	if(',' in raw_line) : continue

	raw_cnt += 1
	#print(raw_cnt)
	#print(raw_line)
	
	if(raw_line.split('|')[2] != "A"):
		continue
	AS_path_str = raw_line.split('|')[6]
	AS_path_str = AS_path_str.replace("{", "")
	AS_path_str = AS_path_str.replace("}", "")
	AS_path = AS_path_str.split(' ')
	
	lastASset = set()
	lastAS = []
	lastAS.append(AS_path[len(AS_path)-1])

	if(lastAS[0] not in as_prefix4_dict.keys()) : continue

	lastASset.add(lastAS[len(lastAS)-1])
	for x in range(len(AS_path)-2, -1, -1) :
		if(AS_path[x] not in lastASset) :
			lastAS.append(AS_path[x])
			lastASset.add(AS_path[x])
		if(len(lastAS) == 4) : break

	raw_prefix_str = raw_line.split('|')[5]
	HJ_type = 0

	if(lastAS[0]+"_"+raw_prefix_str not in not_type_0_set) :
		raw_prefix = ipaddress.ip_network(raw_prefix_str)
		if(':' in raw_prefix_str) :
			if(ipv6_ownership_check(raw_prefix, lastAS[0])) :
				not_type_0_set.add(lastAS[0]+"_"+raw_prefix_str)
				HJ_type = -1
		else :
			if(ipv4_ownership_check(raw_prefix, lastAS[0])) :
				not_type_0_set.add(lastAS[0]+"_"+raw_prefix_str)
				HJ_type = -1


		if(HJ_type == 0) :
			#result.write(raw_line + '\n')
			result.write(raw_line + " type_" + str(HJ_type) + '\n')
			continue

	if(len(lastAS)<2) : continue
	if(lastAS[1] not in as_prefix4_dict.keys()) : continue
	HJ_type = 1
	asn1 = int(lastAS[0])
	asn2 = int(lastAS[1])
	if(asn1 > asn2) :
		rel_str = str(asn2) + "-" + str(asn1)
	else :
		rel_str = str(asn1) + "-" + str(asn2)
	if(rel_str not in as_rel_set) :
		if(lastAS[1]+"_"+raw_prefix_str not in not_type_0_set) :
			raw_prefix = ipaddress.ip_network(raw_prefix_str)
			if(':' in raw_prefix_str) :
				if(ipv6_ownership_check(raw_prefix, lastAS[1])) :
					not_type_0_set.add(lastAS[1]+"_"+raw_prefix_str)
					HJ_type = -1
			else :
				if(ipv4_ownership_check(raw_prefix, lastAS[1])) :
					not_type_0_set.add(lastAS[1]+"_"+raw_prefix_str)
					HJ_type = -1
			if(HJ_type == 1) :
				result.write(raw_line + " type_" + str(HJ_type) + '\n')
				continue
	if(len(lastAS)<3) : continue
	if(lastAS[2] not in as_prefix4_dict.keys()) : continue
	HJ_type = 2
	asn1 = int(lastAS[1])
	asn2 = int(lastAS[2])	
	if(asn1 > asn2) :
		rel_str = str(asn2) + "-" + str(asn1)
	else :
		rel_str = str(asn1) + "-" + str(asn2)
	if(rel_str not in as_rel_set) :
		if(lastAS[2]+"_"+raw_prefix_str not in not_type_0_set) :
			raw_prefix = ipaddress.ip_network(raw_prefix_str)
			if(':' in raw_prefix_str) :
				if(ipv6_ownership_check(raw_prefix, lastAS[2])) :
					not_type_0_set.add(lastAS[2]+"_"+raw_prefix_str)
					HJ_type = -1
			else :
				if(ipv4_ownership_check(raw_prefix, lastAS[2])) :
					not_type_0_set.add(lastAS[2]+"_"+raw_prefix_str)
					HJ_type = -1
			if(HJ_type == 2) :
				result.write(raw_line + " type_" + str(HJ_type) + '\n')
				continue
	if(len(lastAS)<4) : continue
	if(lastAS[3] not in as_prefix4_dict.keys()) : continue
	HJ_type = 3
	asn1 = int(lastAS[2])
	asn2 = int(lastAS[3])	
	if(asn1 > asn2) :
		rel_str = str(asn2) + "-" + str(asn1)
	else :
		rel_str = str(asn1) + "-" + str(asn2)
	if(rel_str not in as_rel_set) :
		if(lastAS[3]+"_"+raw_prefix_str not in not_type_0_set) :
			raw_prefix = ipaddress.ip_network(raw_prefix_str)
			if(':' in raw_prefix_str) :
				if(ipv6_ownership_check(raw_prefix, lastAS[3])) :
					not_type_0_set.add(lastAS[3]+"_"+raw_prefix_str)
					HJ_type = -1
			else :
				if(ipv4_ownership_check(raw_prefix, lastAS[3])) :
					not_type_0_set.add(lastAS[3]+"_"+raw_prefix_str)
					HJ_type = -1
			if(HJ_type == 3) :
				result.write(raw_line + " type_" + str(HJ_type) + '\n')
				continue

#os.system("sudo rm /data/BGP_LOG/"+date_site+"/"+date_site+ris_site+".txt")
result.close()
