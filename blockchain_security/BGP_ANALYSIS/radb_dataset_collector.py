import os
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


data_path = "/data/BGP_LOG/prefix-radb/"
cnt = 0

asn_file = "/data/BGP_LOG/all-asn"
with open(asn_file) as f :
	content = f.readlines()
asn_list = [x.strip() for x in content]


start = int(sys.argv[1])

end = int(sys.argv[2])


for i in range(start, end) :
	asn = asn_list[i]
	print(i)
	os.system("whois -h whois.radb.net -- '-i origin AS" + str(asn) + "' | grep route:\  | awk -F' ' '{print $2}' > " + data_path + asn)
	os.system("whois -h whois.radb.net -- '-i origin AS" + str(asn) + "' | grep route6:\  | awk -F' ' '{print $2}' >> " + data_path + asn)
	#print(str(cnt) + " : "  + i)


