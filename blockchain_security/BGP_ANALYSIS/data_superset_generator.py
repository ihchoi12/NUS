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


#date = sys.argv[1]
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


as_prefix4_dict = dict()
as_prefix6_dict = dict()

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
			as_prefix6_dict[i].add(j)
		elif('.' in j) :
			as_prefix4_dict[i].add(j)

ripe_stat_dat_path = "/data/BGP_LOG/AS-prefix-dataset/prefix-ripe-stat"
with open(ripe_stat_dat_path) as f :
	content = f.readlines()
prefix_list = [x.strip() for x in content]
for j in prefix_list :
	asn = j.split(' ')[0]
	if(asn not in as_prefix4_dict.keys()) : continue
	prefix_str = j.split(' ')[1]
	if(':' in prefix_str) :
		as_prefix6_dict[i].add(prefix_str)
	elif('.' in prefix_str) :	
		as_prefix4_dict[i].add(prefix_str)

ipv4_routeviews_plus_ipinfo_path = "/data/BGP_LOG/AS-prefix-dataset/routeviews_plus_ipinfo_IPv4/"

for i in os.listdir(ipv4_routeviews_plus_ipinfo_path) : # i is string
	if(i not in as_prefix4_dict.keys()) : continue
	with open(ipv4_routeviews_plus_ipinfo_path + i) as f :
		content = f.readlines()
	prefix_list = [x.strip() for x in content]

	for j in prefix_list :
		if('.' not in j) : continue
		as_prefix4_dict[i].add(j)

ipv6_routeviews_plus_ipinfo_path = "/data/BGP_LOG/AS-prefix-dataset/routeviews_plus_ipinfo_IPv6/"
for i in os.listdir(ipv6_routeviews_plus_ipinfo_path) : # i is string
	if(i not in as_prefix4_dict.keys()) : continue
	with open(ipv6_routeviews_plus_ipinfo_path + i) as f :
		content = f.readlines()
	prefix_list = [x.strip() for x in content]

	for j in prefix_list :
		as_prefix6_dict[i].add(j)

result_ipv4_path = "/data/BGP_LOG/AS-prefix-dataset/prefix-superset/prefix_ipv4_superset"
result_ipv4 = open(result_ipv4_path, 'w')
for i in as_prefix4_dict.keys() :
	for j in as_prefix4_dict[i] :
		result_ipv4.write(i + "," + j + '\n')


result_ipv6_path = "/data/BGP_LOG/AS-prefix-dataset/prefix-superset/prefix_ipv6_superset"
result_ipv6 = open(result_ipv6_path, 'w')
for i in as_prefix6_dict.keys() :
	for j in as_prefix6_dict[i] :
		result_ipv6.write(i + "," + j + '\n')


#############ABOVE : DATA IMPORTIMG##################
