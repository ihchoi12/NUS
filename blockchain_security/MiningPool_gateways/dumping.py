
import csv
import json
import requests
from datetime import timedelta, date
import time
import operator




date_list = []
def daterange(date1, date2):
    for n in range(int ((date2 - date1).days)+1):
        yield date1 + timedelta(n)

start_dt = date(2018, 6, 16)
end_dt = date(2018, 6, 30)
for dt in daterange(start_dt, end_dt):
    date_list.append(dt.strftime("%Y%m%d"))




#############################################################
#       date generate   from 20180101 to 20180630           #
#############################################################


for x in date_list:
    f = open(x+".csv", 'w')
    filewriter = csv.writer(f, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
    var_url = 'https://chain.api.btc.com/v3/block/date/' + x
    response = requests.get(var_url)
    json_data = json.loads(response.text)
    data_list = json_data[u'data']


    for y in data_list :

        var_url = 'https://bitnodes.earn.com/api/v1/inv/' + y[u'hash'] + '/'
        response = requests.get(var_url)
        json_data = json.loads(response.text)
        print y[u'height']
        if json_data.get(u'stats') != None :
            ip_list = list([y[u'height'], y[u'hash'].encode("UTF-8"), y[u'extras'][u'pool_name'].encode("UTF-8")])
            for z in json_data[u'stats'][u'head'] :
                ip_list.append(z[0].encode("UTF-8"))
            filewriter.writerow(ip_list)

        else :
            print json_data
            filewriter.writerow([y[u'height'], y[u'hash'], y[u'extras'][u'pool_name'], "Not Found"])

        time.sleep(4)

    f.close()
