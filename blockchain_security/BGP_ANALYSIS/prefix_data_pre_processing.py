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
	Returns boolean: is `a` a subnet of `b`? && there are diffrent each other
	"""
	a = ipaddress.ip_network(a)
	b = ipaddress.ip_network(b)
	a_len = a.prefixlen
	b_len = b.prefixlen
	return a_len > b_len and a.supernet(a_len - b_len) == b

def prefix_data_processor(data_path) :
	global asn_prefix_dict
	with open(data_path) as f :
		content = f.readlines()
	data_list = [x.strip() for x in content]
	for i in data_list :
		asn = i.split(',')[0]
		prefix_str = i.split(',')[1]
		if("/" not in prefix_str) : continue
		if(':' in prefix_str) :
			#if(':' not in prefix) : continue
			prefix_real = ipaddress.ip_network(prefix_str, strict=False)
			if(prefix_real.prefixlen > 32) :
				prefix_real = prefix_real.supernet(new_prefix=32)
			else :
				prefix_real = prefix_real.supernet(new_prefix=prefix_real.prefixlen-2)

		else :
			#if('.' not in prefix) : continue
			prefix_str = prefix_str.split(".")[0] + "." + prefix_str.split(".")[1] + ".0.0/" + prefix_str.split("/")[1]
			prefix_real = ipaddress.ip_network(prefix_str)
			if(prefix_real.prefixlen > 16) :
				prefix_real = prefix_real.supernet(new_prefix=16)
			else :
				prefix_real = prefix_real.supernet(new_prefix=prefix_real.prefixlen-1)
		if(asn not in asn_prefix_dict.keys()) :
			asn_prefix_dict[asn] = set()
		asn_prefix_dict[asn].add(prefix_real)

asn_prefix_dict = dict()

all_asn_path = "/data/BGP_LOG/all-asn.txt"
with open(all_asn_path) as f :
	content = f.readlines()
asn_set = {x.strip() for x in content}

for asn in asn_set :
	asn_prefix_dict[asn] = set()



data_path = "/data/BGP_LOG/AS-prefix-dataset/prefix-HE.txt"
prefix_data_processor(data_path)
data_path = "/data/BGP_LOG/AS-prefix-dataset/prefix-ipinfo.txt"
prefix_data_processor(data_path)
#data_path = "/data/BGP_LOG/AS-prefix-dataset/prefix-ripe-stat.txt"
#prefix_data_processor(data_path)
data_path = "/data/BGP_LOG/AS-prefix-dataset/prefix-routeviews.txt"
prefix_data_processor(data_path)

radb_data_path = "/data/BGP_LOG/AS-prefix-dataset/prefix-radb/"


for i in os.listdir(radb_data_path) : # i is string
	#print(i)

	asn = i
	with open(radb_data_path + i) as f :
		content = f.readlines()
	data_set = {x.strip() for x in content}
	for prefix_str in data_set :
		if("/" not in prefix_str) : continue
		if(':' in prefix_str) :
			#if(':' not in prefix) : continue
			prefix_real = ipaddress.ip_network(prefix_str, strict=False)
			if(prefix_real.prefixlen > 32) :
				prefix_real = prefix_real.supernet(new_prefix=32)
			else :
				prefix_real = prefix_real.supernet(new_prefix=prefix_real.prefixlen-2)

		else :
			#if('.' not in prefix) : continue
			prefix_str = prefix_str.split(".")[0] + "." + prefix_str.split(".")[1] + ".0.0/" + prefix_str.split("/")[1]
			prefix_real = ipaddress.ip_network(prefix_str)
			if(prefix_real.prefixlen > 16) :
				prefix_real = prefix_real.supernet(new_prefix=16)
			else :
				prefix_real = prefix_real.supernet(new_prefix=prefix_real.prefixlen-1)
		if(asn not in asn_prefix_dict.keys()) :
			asn_prefix_dict[asn] = set()
		asn_prefix_dict[asn].add(prefix_real)

ntt_data_path = "/data/BGP_LOG/AS-prefix-dataset/prefix-ntt/"

for i in os.listdir(ntt_data_path) : # i is string
	#print(i)

	asn = i.split('.')[0]
	with open(ntt_data_path + i) as f :
		content = f.readlines()
	data_set = {x.strip() for x in content}
	for prefix_str in data_set :
		if("/" not in prefix_str) : continue
		if(':' in prefix_str) :
			#if(':' not in prefix) : continue
			prefix_real = ipaddress.ip_network(prefix_str, strict=False)
			if(prefix_real.prefixlen > 32) :
				prefix_real = prefix_real.supernet(new_prefix=32)
			else :
				prefix_real = prefix_real.supernet(new_prefix=prefix_real.prefixlen-2)

		else :
			#if('.' not in prefix) : continue
			prefix_str = prefix_str.split(".")[0] + "." + prefix_str.split(".")[1] + ".0.0/" + prefix_str.split("/")[1]
			prefix_real = ipaddress.ip_network(prefix_str)
			if(prefix_real.prefixlen > 16) :
				prefix_real = prefix_real.supernet(new_prefix=16)
			else :
				prefix_real = prefix_real.supernet(new_prefix=prefix_real.prefixlen-1)
		if(asn not in asn_prefix_dict.keys()) :
			asn_prefix_dict[asn] = set()
		asn_prefix_dict[asn].add(prefix_real)


for i in asn_prefix_dict.keys() : # i is string
	print(i)

	result_path = "/data/BGP_LOG/AS-prefix-dataset/prefix-superset/temp3/" + i + ".txt"
	result = open(result_path, 'w')

	for j in asn_prefix_dict[i] :
		check = 0
		for k in asn_prefix_dict[i] :
			if(is_subnet_of(j, k)) :
				check = 1
				break
		if(check == 0) :
			result.write(str(j) + '\n')
	result.close()