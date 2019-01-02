#!/usr/bin/env python
import os, sys
from os import listdir
from os.path import isfile, join
import shlex, subprocess
from collections import defaultdict
from ipaddress import ip_network
import ipaddress

date = sys.argv[1]
collector = sys.argv[2]
timestamp = sys.argv[3]

bgp_raw_file_name = "/data/RIS-DATA/"+date+"/"+collector+"/updates."+date+"."+timestamp+".gz"
temp_text_file_name = "/data/tmp/updates."+date+"."+timestamp+"."+collector+".gz"
if not os.path.isfile(bgp_raw_file_name):
	sys.exit()
def bgpdump(rawfile):
	command = "./ripencc-bgpdump-99da8741c8c8/bgpdump -m "+bgp_raw_file_name+" | grep '|A|' | awk -F'|' '{print $2, $6, $7}' | sort | uniq"
	# print command
	ps = subprocess.Popen(command,shell=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
	output = ps.communicate()[0]
	output = output.strip()
	return output.decode().split("\n")

announcements =  bgpdump(bgp_raw_file_name)


as_relationship_file = "asn-peer-all.csv"
as_prefix_file = "asn-prefix-all-cleaned.csv"
def load_as_rel_data(asn, as_rel_dict):
	filename = "./asn-peer/"+str(asn)+".txt"
	if not os.path.isfile(filename):
		return as_rel_dict
	with open(filename) as f:
		line_list = f.readlines()
	line_list = [x.strip() for x in line_list]
	as_rel_dict[asn] = []
	for line in line_list:
		peer = int(line)
		as_rel_dict[asn].append(peer)
	return as_rel_dict

def load_as_prefix_data(asn, as_prefix_dict):
	filename = "./asn-prefix/"+str(asn)+".txt"
	if not os.path.isfile(filename):
		return as_prefix_dict
	with open(filename) as f:
		line_list = f.readlines()
	line_list = [x.strip() for x in line_list]
	as_prefix_dict[asn] = dict()
	# as_prefix_dict_16[asn] = []
	for line in line_list:
		# as_prefix_dict[asn].append(line)
		prefix_16 = ""
		if "." in line:
			prefix_16 = line.split(".")[0]+":"+line.split(".")[1]
		elif ":" in line:
			prefix_16 = line.split(":")[0]+":"+line.split(":")[1]
		if prefix_16 != "":
			if prefix_16 not in as_prefix_dict[asn]:
				as_prefix_dict[asn][prefix_16] = [line]
			else:
				as_prefix_dict[asn][prefix_16].append(line)
			# as_prefix_dict_16[asn].append([prefix_16])
	return as_prefix_dict


def is_subnet_of(a, b):
	"""
	Returns boolean: is `a` a subnet of `b`?
	"""
	a = ipaddress.ip_network(a)
	b = ipaddress.ip_network(b)
	a_len = a.prefixlen
	b_len = b.prefixlen
	return a_len >= b_len and a.supernet(a_len - b_len) == b


as_rel_dict = dict()
as_prefix_dict = dict()
as_prefix_dict_16 = dict()

type_1_results = dict()
type_2_results = dict()

for line in announcements:
	if "syslog" in line:
		continue
	line_arr = line.split(" ")
	prefix = line_arr[1]
	last_ASes_str = line_arr[-1]

	save_string_type_1 = prefix + " " + last_ASes_str
	if save_string_type_1 in type_1_results:
		type_1_results[save_string_type_1].append(line)
		continue
	last_ASes = [int(x) for x in line_arr[-1].replace("{","").replace("}","").split(",")]

	second_last = len(line_arr)-2
	if second_last <= 2 :
		continue
	while second_last > 2 and int(line_arr[second_last]) in last_ASes:
		second_last -= 1

	second_last_AS = int(line_arr[second_last])

	save_string_type_2 = prefix + " " + str(second_last_AS)+" " + last_ASes_str
	if save_string_type_2 in type_2_results:
		type_2_results[save_string_type_2].append(line)
		continue


	for last_AS in last_ASes:
		if last_AS not in as_prefix_dict: 
			as_prefix_dict= load_as_prefix_data(last_AS, as_prefix_dict)
	
	prefix_16 = ""
	if "." in prefix:
		prefix_16 = prefix.split(".")[0]+":"+prefix.split(".")[1]
	elif ":" in prefix:
		prefix_16 = prefix.split(":")[0]+":"+prefix.split(":")[1]

	own_prefix = False
	for last_AS in last_ASes:
		if last_AS not in as_prefix_dict:
			own_prefix = True # Until we have full dataset, this is still ok.
			continue
		if prefix_16 in as_prefix_dict[last_AS].keys(): #Super conservative
			own_prefix = True
			# for last_AS_prefix in as_prefix_dict[last_AS][prefix_16]:
			# 	if is_subnet_of(prefix, last_AS_prefix):
			# 		own_prefix = True
			# 		break
			if own_prefix:
				break;
			
	if not own_prefix:
		# print line, "type_1"
		save_string = prefix + " " + last_ASes_str
		type_1_results[save_string] = [line]
	else:
		is_peer = False
		if second_last_AS not in as_rel_dict:
			as_rel_dict = load_as_rel_data(second_last_AS, as_rel_dict)
		if second_last_AS not in as_rel_dict:
			continue
		for last_AS in last_ASes:
			if last_AS not in as_rel_dict:
				as_rel_dict = load_as_rel_data(last_AS, as_rel_dict)
			if last_AS not in as_rel_dict:
				is_peer = True
				continue #Until we have full dataset, this is not OK because there is no relationship recorded.
			# print second_last_AS, as_rel_dict[last_AS]
			if second_last_AS in as_rel_dict[last_AS] or last_AS in as_rel_dict[second_last_AS]:
				is_peer = True
				break
		if not is_peer:
			# print own_prefix, line, "type2"
			save_string = prefix + " " + str(second_last_AS)+" " + last_ASes_str
			type_2_results[save_string] = [line]

print len(announcements), len(type_1_results) + len(type_2_results)

output = open("/data/muoi/bgp-hijacking/result-"+date+"."+timestamp+"."+collector+".txt","w+")

for key in type_1_results.keys():
	for line in type_1_results[key]:
		# print line, "type_1"
		output.write(str(line) + " type_1 \n")
for key in type_2_results.keys():
	for line in type_2_results[key]:
		# print line, "type_2"
		output.write(str(line) + " type_2 \n")