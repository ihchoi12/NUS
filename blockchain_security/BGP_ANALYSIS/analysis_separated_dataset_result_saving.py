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

start = time.time()


prefix_data_path = "/data/BGP_LOG/AS-prefix-dataset/prefix-superset/supernet_for_bigger_only/"
peering_data_path = "/data/BGP_LOG/AS_RELATIONSHIP_DATA/peer_data/peering_for_each_ASN/"

def is_subnet_of(a, b):
    """
    Returns boolean: is `a` a subnet of `b`?
    """
    a = ipaddress.ip_network(a)
    b = ipaddress.ip_network(b)
    a_len = a.prefixlen
    b_len = b.prefixlen
    return a_len >= b_len and a.supernet(a_len - b_len) == b

def prefix_ownership_check(prefix, asn) :
    with open(prefix_data_path + asn + ".txt") as f :
        content = f.readlines()
    prefix_set = {x.strip() for x in content}
    for prefix_str in prefix_set :
        prefix_real = ipaddress.ip_network(prefix_str) 
        if(is_subnet_of(prefix, prefix_real)) :
            return True
    return False



all_asn_path = "/data/BGP_LOG/all-asn.txt"
with open(all_asn_path) as f :
    content = f.readlines()
asn_set = {x.strip() for x in content}


fixed_results_dict = dict()



date_list = []
def daterange(date1, date2):
    for n in range(int ((date2 - date1).days)+1):
        yield date1 + timedelta(n)

start_dt = date(2018, 11, 1)
end_dt = date(2018, 11, 1)
for dt in daterange(start_dt, end_dt):
    date_list.append(dt.strftime("%Y%m%d"))

for date in date_list :
    print(date)



    result_path = "/data/BGP_LOG/raw_data_analysis/result/raw_Ntype_" + date + ".txt"
    result = open(result_path, 'w')

    #ris_data_path = "/data/BGP_LOG/hijacking_include_BTC/" + date + "/" + "20181022ALL1800"
    ris_data_path = "/data/BGP_LOG/raw_data_analysis/merged_raw_remove_redundancy_" + date + ".txt"
    with open(ris_data_path) as f :
        content = f.readlines()
    raw_line_list = [x.strip() for x in content]
    print("analysis start!")

    not_type_0_set = set()
    cnt = 0
    for raw_line in raw_line_list :
        cnt+=1
        print(cnt)
        #print(str(cnt) + " : " + raw_line)
        if("BGP4MP" not in raw_line) : continue
        if(',' in raw_line) : continue
        if('_' in raw_line) : continue
        

        
        raw_prefix_str = raw_line.split('|')[5] # prefix part of the announcement
        AS_path_str = raw_line.split('|')[6] # AS-path part of the announcement
        
        if(':' in raw_prefix_str) :
            key_str = raw_prefix_str + "-" + AS_path_str
        elif('.' in raw_prefix_str) :
            if(int(raw_prefix_str.split('/')[1]) >= 16) :
                key_str = raw_prefix_str.split('.')[0] + '.' +  raw_prefix_str.split('.')[1] + "-" + AS_path_str
            else :
                key_str = raw_prefix_str + "-" + AS_path_str
        # to save previous fixed result ==> will be used to check following cases quickly
        if(key_str in fixed_results_dict.keys()) :
            #print("hi")
            if(fixed_results_dict[key_str] != "X") :
                result.write(raw_line + " type_" + fixed_results_dict[key_str] + '\n')
            continue

        if(raw_line.split('|')[2] != "A"):
            continue
        AS_path_str = AS_path_str.replace("{", "")
        AS_path_str = AS_path_str.replace("}", "")
        AS_path = AS_path_str.split(' ')

        lastASset = set()
        lastAS = []
        lastAS.append(AS_path[len(AS_path)-1])

        lastASset.add(lastAS[len(lastAS)-1])
        for x in range(len(AS_path)-2, -1, -1) : # get last 4 ASes 
            if(AS_path[x] not in lastASset) :
                lastAS.append(AS_path[x])
                lastASset.add(AS_path[x])
            if(len(lastAS) == 4) : break

        
        HJ_type = 0
        
        if(lastAS[0] not in asn_set) :
            fixed_results_dict[key_str] = "X" 
            continue # last AS not in the ASN set.. ignore

        if(lastAS[0]+"_"+raw_prefix_str not in not_type_0_set) :
            raw_prefix = ipaddress.ip_network(raw_prefix_str)
            if(prefix_ownership_check(raw_prefix, lastAS[0])) : # last AS own the prefix.. not Hijacking
                not_type_0_set.add(lastAS[0]+"_"+raw_prefix_str) # add to the not type_0 set.. to save time afterwards
                HJ_type = -1
            if(HJ_type == 0) :
                #result.write(raw_line + '\n')
                result.write(raw_line + " type_" + str(HJ_type) + '\n')
                fixed_results_dict[key_str] = "0"
                continue


        if(len(lastAS)<2) :
            fixed_results_dict[key_str] = "X" 
            continue # cannot check type 1,2,3
        if(lastAS[1] not in asn_set) :
            fixed_results_dict[key_str] = "X" 
            continue # no data for the 2nd last ASN
        HJ_type = 1
        asn1 = lastAS[0]
        asn2 = lastAS[1]
        if(int(asn1) > int(asn2)) :
            temp = asn1
            asn1 = asn2
            asn2 = temp
        with open(peering_data_path + asn1 + ".txt") as f :
            content = f.readlines()
        peers_set = {x.strip() for x in content}
        if(asn2 not in peers_set) : # No peering relation between 'the last ASN' and '2nd last ASN' 
            if(lastAS[1]+"_"+raw_prefix_str not in not_type_0_set) :
                raw_prefix = ipaddress.ip_network(raw_prefix_str)
                if(prefix_ownership_check(raw_prefix, lastAS[1])) : # 2nd last AS own the prefix.. not type_1
                    not_type_0_set.add(lastAS[1]+"_"+raw_prefix_str) # add to the not type_0 set.. to save time afterwards
                    HJ_type = -1
                if(HJ_type == 1) :
                    #result.write(raw_line + '\n')
                    result.write(raw_line + " type_" + str(HJ_type) + '\n')
                    fixed_results_dict[key_str] = "1"
                    continue


        if(len(lastAS)<3) :
            fixed_results_dict[key_str] = "X" 
            continue # cannot check type 2,3
        if(lastAS[2] not in asn_set) : 
            fixed_results_dict[key_str] = "X"
            continue # no data for the 3rd last ASN
        HJ_type = 2
        asn1 = lastAS[1]
        asn2 = lastAS[2]
        if(int(asn1) > int(asn2)) :
            temp = asn1
            asn1 = asn2
            asn2 = temp
        with open(peering_data_path + asn1 + ".txt") as f :
            content = f.readlines()
        peers_set = {x.strip() for x in content}
        if(asn2 not in peers_set) : # No peering relation between '2nd last ASN' and '3rd last ASN' 
            if(lastAS[2]+"_"+raw_prefix_str not in not_type_0_set) :
                raw_prefix = ipaddress.ip_network(raw_prefix_str)
                if(prefix_ownership_check(raw_prefix, lastAS[2])) : # 3rd last AS own the prefix.. not type_2
                    not_type_0_set.add(lastAS[2]+"_"+raw_prefix_str) # add to the not type_0 set.. to save time afterwards
                    HJ_type = -1
                if(HJ_type == 2) :
                    #result.write(raw_line + '\n')
                    result.write(raw_line + " type_" + str(HJ_type) + '\n')
                    fixed_results_dict[key_str] = "2"
                    continue

        if(len(lastAS)<4) :
            fixed_results_dict[key_str] = "X" 
            continue # cannot check type 3
        if(lastAS[3] not in asn_set) :
            fixed_results_dict[key_str] = "X" 
            continue # no data for the 4th last ASN
        HJ_type = 3
        asn1 = lastAS[2]
        asn2 = lastAS[3]
        if(int(asn1) > int(asn2)) :
            temp = asn1
            asn1 = asn2
            asn2 = temp
        with open(peering_data_path + asn1 + ".txt") as f :
            content = f.readlines()
        peers_set = {x.strip() for x in content}
        if(asn2 not in peers_set) : # No peering relation between '3rd last ASN' and '4th last ASN' 
            if(lastAS[3]+"_"+raw_prefix_str not in not_type_0_set) :
                raw_prefix = ipaddress.ip_network(raw_prefix_str)
                if(prefix_ownership_check(raw_prefix, lastAS[3])) : # 4th last AS own the prefix.. not type_3
                    not_type_0_set.add(lastAS[3]+"_"+raw_prefix_str) # add to the not type_0 set.. to save time afterwards
                    HJ_type = -1
                if(HJ_type == 3) :
                    #result.write(raw_line + '\n')
                    result.write(raw_line + " type_" + str(HJ_type) + '\n')
                    fixed_results_dict[key_str] = "3"
                    continue
        fixed_results_dict[key_str] = "X"

    print(timestamp + " is done!!!")
    result.close()
    print(fixed_results_dict)

end = time.time()
print(end - start)