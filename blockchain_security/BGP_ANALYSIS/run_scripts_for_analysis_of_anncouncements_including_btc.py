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


date_list = []
def daterange(date1, date2):
    for n in range(int ((date2 - date1).days)+1):
        yield date1 + timedelta(n)

start_dt = date(2018, 11, 2)
end_dt = date(2018, 11, 30)
for dt in daterange(start_dt, end_dt):
	date_list.append(dt.strftime("%Y%m%d"))
for date in date_list :
	os.system("sudo mkdir /data/BGP_LOG/hijacking_include_BTC/analysis_with_oneday_superset/" + date)
	os.system("sudo chmod +777 /data/BGP_LOG/hijacking_include_BTC/analysis_with_oneday_superset/" + date)

	for num in range(0, 24) :
		if(num<10) : 
			H = "0" + str(num)
		else :
			H = str(num)

		os.system("sh " + date + "_" + H + ".sh")
		print(date + " : " + H + " is done!!!")
		time.sleep(40)