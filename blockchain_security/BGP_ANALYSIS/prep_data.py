#!/usr/bin/env python
import os, sys
from os import listdir
from os.path import isfile, join
import shlex, subprocess
from collections import defaultdict

# as_relationship_file = "asn-peer-all-additional.csv"
as_relationship_file = "/home/inho/BGP_ANALYSIS/AS_RELATIONSHIP/peer_data/merged_data.txt"
as_prefix_file = "asn-prefix-all-additional.csv"
def load_as_rel_data(filename):
	with open(filename) as f:
		line_list = f.readlines()
	line_list = [x.strip() for x in line_list]
	as_rel_dict = dict()
	for line in line_list:
		asn1 = int(line.split(" ")[0])
		asn2 = int(line.split(" ")[1])
		if asn1 not in as_rel_dict:
			as_rel_dict[asn1] = [asn2]
		else:
			if asn2 not in as_rel_dict[asn1]:
				as_rel_dict[asn1].append(asn2)
		if asn2 not in as_rel_dict:
			as_rel_dict[asn2] = [asn1]
		else:
			if asn1 not in as_rel_dict[asn2]:
				as_rel_dict[asn2].append(asn1)
	return as_rel_dict

# def load_as_prefix_data(filename):

# 	with open(filename) as f:
# 		line_list = f.readlines()
# 	line_list = [x.strip() for x in line_list]
# 	as_prefix_dict = dict()
# 	for line in line_list:
# 		asn = int(line.split(",")[0])
# 		prefix=line.split(",")[1]
# 		if asn not in as_prefix_dict:
# 			as_prefix_dict[asn] = [prefix]
# 		else:
# 			if prefix not in as_prefix_dict[asn]:
# 				as_prefix_dict[asn].append(prefix)
# 	return as_prefix_dict


as_rel_dict = load_as_rel_data(as_relationship_file)
# as_prefix_dict = load_as_prefix_data(as_prefix_file)

# print as_rel_dict.keys()

for asn in as_rel_dict.keys():
	output = open("./asn-peer/"+str(asn)+".txt","w+")
	for peer in as_rel_dict[asn]:
		output.write(str(peer)+"\n")

# for asn in as_prefix_dict.keys():
# 	output = open("./asn-prefix/"+str(asn)+".txt","w+")
# 	for prefix in as_prefix_dict[asn]:
# 		output.write(str(prefix)+"\n")