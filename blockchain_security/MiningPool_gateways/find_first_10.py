import csv
import json
import requests
from datetime import timedelta, date
import time
import operator
import csv



date_list = []
def daterange(date1, date2):
    for n in range(int ((date2 - date1).days)+1):
        yield date1 + timedelta(n)

start_dt = date(2018, 1, 1)
end_dt = date(2018, 1, 1)
for dt in daterange(start_dt, end_dt):
    date_list.append(dt.strftime("%Y%m%d"))

#############################################################
#       date generate   from 20180101 to 20180630           #
#############################################################

cnt = 0
data_list = list()
final_dict = dict()
for x in date_list:
    cnt+=1

    f = open(x+'_test.csv', 'r')
    rdr = csv.reader(f)

    for line in rdr:

        data_list.append(line)

    #print data_list

    if cnt % 1 == 0 :
        first_node_dict = dict()
        for y in data_list :
            if first_node_dict.get(y[2]) == None :
                first_node_dict[y[2]] = dict()

            if first_node_dict[y[2]].get(y[3]) == None :
                first_node_dict[y[2]][y[3]] = 1
            else :
                first_node_dict[y[2]][y[3]] += 1

        for y in first_node_dict.keys() :
            if final_dict.get(y) == None :
                final_dict[y] = list()
            for z in first_node_dict[y].keys() :
                print y + " " + z + " " + str(first_node_dict[y][z]) + " " + str(float(max(first_node_dict[y].values()))/float(2)) 
                if first_node_dict[y][z] > float(max(first_node_dict[y].values()))/float(2) :
                    final_dict[y].append(z)


        print final_dict

    f.close()




'''

with open('gateway.csv', 'wb') as csvfile:
    filewriter = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)

    final_dict = dict()

    cnt = 0
    data_list = list()
    data_dict = dict()
    for x in date_list:
        cnt+=1
        var_url = 'https://chain.api.btc.com/v3/block/date/' + x
        print var_url
        response = requests.get(var_url)

        json_data = json.loads(response.text)
        data_list = json_data[u'data']
        for y in data_list :
            if y[u'extras'][u'pool_name'] != u'unknown' :
                data_dict[y[u'hash']] = y[u'extras'][u'pool_name']
                #print y[u'hash'] + "  " + data_dict[y[u'hash']]
        if cnt % 10 == 0 :
            first_node_dict = dict()

            for y in data_dict.keys():
                pool_name = data_dict[y]
                if first_node_dict.get(pool_name) == None :
                    first_node_dict[pool_name] = dict()

                var_url = 'https://bitnodes.earn.com/api/v1/inv/' + y + '/'
                response = requests.get(var_url)
                json_data = json.loads(response.text)

                if json_data.get(u'stats') != None :
                    first_node_ip = json_data[u'stats'][u'head'][0][0]

                    if first_node_dict[pool_name].get(first_node_ip) == None :
                        first_node_dict[pool_name][first_node_ip] = 1
                    else :
                        first_node_dict[pool_name][first_node_ip] += 1

            for y in first_node_dict.keys() :
                if final_dict.get(y) == None :
                    final_dict[y] = list()
                for z in first_node_dict[y.decode("UTF-8")].keys() :
                    if first_node_dict[y.decode("UTF-8")][z] > float(max(first_node_dict[y.decode("UTF-8")].values()))/float(2) :
                        if final_dict[y].count(z) == 0 :
                            final_dict[y].append(z)
            print final_dict
            cnt = 0
            data_list = list()
            data_dict = dict()

        time.sleep(15)
    for x in final_dict.keys() :
        filewriter.writerow([x, final_dict[x]])
'''
