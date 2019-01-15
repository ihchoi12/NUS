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

start_dt = date(2018, 12, 14)
end_dt = date(2018, 12, 15)
for dt in daterange(start_dt, end_dt):
    date_list.append(dt.strftime("%Y%m%d"))

for i in date_list :
	print(i)
	os.system("sudo python raw_data_prep.py " + i)
	print("raw_data_prep.py FOR " + i + " is done!!!")
	#os.system("sudo python3 bgp_analysis.py " + i)
	#print("bgp_analysis.py FOR " + i + " is done!!!")
	#os.system("sudo cat ./result/suspicious_" + i + ".txt | sort -nk1 | awk '{if(a[$2\"-\"$3]==0){a[$2\"-\"$3]=$1; print $0} else{if($1 - a[$2\"-\"$3] > 120){a[$2\"-\"$3]=$1; print $0;} } }' > ./result/duplX_" + i + ".txt")
	#os.system("sudo sort -u \"result_" + i + ".txt\" -o \"./remove_dupl/result_duplX_" + i + ".txt\"")
	#print("Removing duplicated announcements FOR " + i + " is done!!!")
	#os.system("sudo python3 python_script_to_check_if_prefix_includes_btc_ip.py " + i)
	#print("Analysis for " + i + " has finished!!!")
	#os.system("sudo rm /data/BGP_LOG/" + i + "/*")
	#print("Data for " + i + " has removed!!!")


