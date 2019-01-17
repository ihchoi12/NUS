import csv
import json
import requests
from datetime import timedelta, date
import time
import operator
import os



date_list = []
def daterange(date1, date2):
    for n in range(int ((date2 - date1).days)+1):
        yield date1 + timedelta(n)

start_dt = date(2018, 12, 23)
end_dt = date(2018, 12, 31)
for dt in daterange(start_dt, end_dt):
    date_list.append(dt.strftime("%Y%m%d"))


for i in date_list :
	os.system("sudo cp -r copy_dir " + i)
	print("sudo cp -r copy_dir " + i)
	os.system("sudo chmod -R +777 " + i)
	print("sudo chmod -R +777 " + i)
	os.system("sudo sh rrc.sh " + i)
	print("sudo sh rrc.sh " + i)
	print(i + " is done!!!")
