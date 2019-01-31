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

#which_hour = sys.argv[1]

prefix_data_path = "/data/BGP_LOG/AS-prefix-dataset/prefix-superset/pre_processed_superset/"
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
    
    global asn_prefix_dict
    
    if(asn not in asn_prefix_dict.keys()) :
        asn_prefix_dict[asn] = dict()
        with open(prefix_data_path + asn + ".txt") as f :
            content = f.readlines()
        prefix_set = {x.strip() for x in content}
        for i in prefix_set :
            prefix_header = ""
            if '.' in i :
                if(int(i.split('/')[1]) < 16) :
                    prefix_header = "big_prefix"
                else :
                    prefix_header = i[0:i.index('.', i.index('.') + 1) + 1]
            elif ':' in i :
                if(int(i.split('/')[1]) < 32) :
                    prefix_header = "big_prefix"
                else :
                    prefix_header = i[0:i.index(':', i.index(':') + 1) + 1]
                    if(prefix_header.split(':')[1] == '') :
                        prefix_header = prefix_header.split(':')[0] + ":0:" 
            if(prefix_header not in asn_prefix_dict[asn].keys()) :
                asn_prefix_dict[asn][prefix_header] = set()
            prefix_real = ipaddress.ip_network(i)
            asn_prefix_dict[asn][prefix_header].add(prefix_real)        
    
    announced_prefix = ipaddress.ip_network(prefix)
    


    prefix_header = "big_prefix"
    if(prefix_header in asn_prefix_dict[asn].keys()) :
        for prefix_str in asn_prefix_dict[asn][prefix_header] :
            prefix_real = ipaddress.ip_network(prefix_str) 
            if(is_subnet_of(announced_prefix, prefix_real)) :
                return True

    prefix_header = ""
    if '.' in prefix:
        prefix_header = prefix[0:prefix.index('.', prefix.index('.') + 1) + 1]
        if(int(prefix.split('/')[1]) < 16) : return False
    elif ':' in prefix:
        prefix_header = prefix[0:prefix.index(':', prefix.index(':') + 1) + 1]
        if(int(prefix.split('/')[1]) < 32) : return False
    if(prefix_header in asn_prefix_dict[asn].keys()) : 
        return True

    #for prefix_str in asn_prefix_dict[asn][prefix_header] :
    #    prefix_real = ipaddress.ip_network(prefix_str) 
    #    if(is_subnet_of(announced_prefix, prefix_real)) :
    #        return True
    return False

asn_prefix_dict = dict()

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
end_dt = date(2018, 12, 31)
for dt in daterange(start_dt, end_dt):
    date_list.append(dt.strftime("%Y%m%d"))

for date in date_list :
    #time.sleep(20)
    print(date)



    result_path = "/data/BGP_LOG/hijacking_include_BTC/analysis_with_oneday_superset/fixed_ownership_check/BTC_hijacking_" + date + ".txt"
    result = open(result_path, 'w')

    #ris_data_path = "/data/BGP_LOG/hijacking_include_BTC/" + date + "/" + "20181022ALL1800"
    ris_data_path = "/data/BGP_LOG/hijacking_include_BTC/analysis_with_oneday_superset/remove_redundancy_" + date + ".txt"
    with open(ris_data_path) as f :
        content = f.readlines()
    raw_line_list = [x.strip() for x in content]
    print("analysis start!")

    not_type_0_set = set()
    #cnt = 0
    for raw_line in raw_line_list :
        #cnt+=1
        #print(cnt)
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
            #raw_prefix = ipaddress.ip_network(raw_prefix_str)
            if(prefix_ownership_check(raw_prefix_str, lastAS[0])) : # last AS own the prefix.. not Hijacking
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
                #raw_prefix = ipaddress.ip_network(raw_prefix_str)
                if(prefix_ownership_check(raw_prefix_str, lastAS[1])) : # 2nd last AS own the prefix.. not type_1
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
                #raw_prefix = ipaddress.ip_network(raw_prefix_str)
                if(prefix_ownership_check(raw_prefix_str, lastAS[2])) : # 3rd last AS own the prefix.. not type_2
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
                #raw_prefix = ipaddress.ip_network(raw_prefix_str)
                if(prefix_ownership_check(raw_prefix_str, lastAS[3])) : # 4th last AS own the prefix.. not type_3
                    not_type_0_set.add(lastAS[3]+"_"+raw_prefix_str) # add to the not type_0 set.. to save time afterwards
                    HJ_type = -1
                if(HJ_type == 3) :
                    #result.write(raw_line + '\n')
                    result.write(raw_line + " type_" + str(HJ_type) + '\n')
                    fixed_results_dict[key_str] = "3"
                    continue
        fixed_results_dict[key_str] = "X"

    print(date + " : is done!!!")
    result.close()
    #print(fixed_results_dict)

end = time.time()
print(end - start)