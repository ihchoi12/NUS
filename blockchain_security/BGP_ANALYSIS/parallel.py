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
import sys



date = sys.argv[1]


for num in range(0, 24) :
	if(num<10) : 
		time = "0" + str(num)
	else :
		time = str(num)

	result_path = "./scripts/" + date + "_" + time + ".sh"
	result = open(result_path, 'w')

	ris_file = "./ris_site_list"

	with open(ris_file) as f :
		content = f.readlines()
	ris_list = [x.strip() for x in content]


	for i in ris_list :

		result.write("python3 btc_hijacking_analysis_in_parallel.py " + date + " " + i + " " + time + "00 &\n")
		result.write("python3 btc_hijacking_analysis_in_parallel.py " + date + " " + i + " " + time + "05 &\n")
		result.write("python3 btc_hijacking_analysis_in_parallel.py " + date + " " + i + " " + time + "10 &\n")
		result.write("python3 btc_hijacking_analysis_in_parallel.py " + date + " " + i + " " + time + "15 &\n")
		result.write("python3 btc_hijacking_analysis_in_parallel.py " + date + " " + i + " " + time + "20 &\n")
		result.write("python3 btc_hijacking_analysis_in_parallel.py " + date + " " + i + " " + time + "25 &\n")
		result.write("python3 btc_hijacking_analysis_in_parallel.py " + date + " " + i + " " + time + "30 &\n")
		result.write("python3 btc_hijacking_analysis_in_parallel.py " + date + " " + i + " " + time + "35 &\n")
		result.write("python3 btc_hijacking_analysis_in_parallel.py " + date + " " + i + " " + time + "40 &\n")
		result.write("python3 btc_hijacking_analysis_in_parallel.py " + date + " " + i + " " + time + "45 &\n")
		result.write("python3 btc_hijacking_analysis_in_parallel.py " + date + " " + i + " " + time + "50 &\n")
		result.write("python3 btc_hijacking_analysis_in_parallel.py " + date + " " + i + " " + time + "55 &\n")

	result.close()