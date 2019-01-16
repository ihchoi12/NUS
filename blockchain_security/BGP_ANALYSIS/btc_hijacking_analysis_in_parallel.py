import os, sys
from os import listdir
from os.path import isfile, join
import shlex, subprocess
from collections import defaultdict
from ipaddress import ip_network
import ipaddress
import ipaddress, sys
import sys




date = sys.argv[1]
collector = sys.argv[2]
timestamp = sys.argv[3]

bgp_raw_file_name = "/data/RIS-DATA/"+date+"/"+collector+"/updates."+date+"."+timestamp+".gz"
#temp_text_file_name = "/data/tmp/updates."+date+"."+timestamp+"."+collector+".gz"
if not os.path.isfile(bgp_raw_file_name):
    sys.exit()
def bgpdump(rawfile):
    command = "./HIJACK-ANALYSIS/ripencc-bgpdump-99da8741c8c8/bgpdump -m "+bgp_raw_file_name+" | grep '|A|' | awk -F'|' '{print $0}' | sort | uniq"
    # print command
    ps = subprocess.Popen(command,shell=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
    output = ps.communicate()[0]
    output = output.strip()
    return output.decode().split("\n")

announcements = bgpdump(bgp_raw_file_name)

#print (announcements[0])


btc_ip_file = "/data/BGP_LOG/bitnodes_last_60days/per_day_superset_of_btc_ipaddr/superset_" + date + ".txt"
with open(btc_ip_file) as f:
    content = f.readlines()
btc_ip_list = [x.strip() + ":8333" for x in content]

btc_ip_header_set = set()
btc_ip_header_dict = dict()

for btc_ip in btc_ip_list:
    btc_ip = btc_ip[0:btc_ip.rfind(':')]
    btc_ip = btc_ip.strip('[]')

    if 'onion' in btc_ip:
        continue

    if '.' in btc_ip:
        btc_ip_header = btc_ip[0:btc_ip.index('.', btc_ip.index('.') + 1) + 1]
    elif ':' in btc_ip:
        btc_ip_header = btc_ip[0:btc_ip.index(':', btc_ip.index(':') + 1) + 1]
    btc_ip_header_set.add(btc_ip_header)
    if btc_ip_header not in btc_ip_header_dict:
        btc_ip_header_dict[btc_ip_header] = list()
    btc_ip_header_dict[btc_ip_header].append(btc_ip)



result_path = "/data/BGP_LOG/hijacking_include_BTC/analysis_with_oneday_superset/" + date + "/" + date + collector + timestamp
result_file = open(result_path, 'w')





for raw_line in announcements :
    if("BGP4MP" not in raw_line) : continue
    #print(raw_line)
    prefix = raw_line.split('|')[5]
    prefix_header = ""
    if '.' in prefix:
        prefix_header = prefix[0:prefix.index('.', prefix.index('.') + 1) + 1]
    elif ':' in prefix:
        prefix_header = prefix[0:prefix.index(':', prefix.index(':') + 1) + 1]
    if prefix_header in btc_ip_header_set:

        btc_ip_included = False
        btc_ip_set = set()
        for btc_ip in btc_ip_header_dict[prefix_header]:
            if ipaddress.ip_address(btc_ip) in ipaddress.ip_network(prefix):
                btc_ip_set.add(btc_ip)
                btc_ip_included = True
        if btc_ip_included:
            result_file.write(raw_line + '\n')
print(timestamp + " is done!!!")
result_file.close()

