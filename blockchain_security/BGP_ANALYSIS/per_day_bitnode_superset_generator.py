from datetime import datetime
#ts = int("1545546545")

# if you encounter a "year is out of range" error the timestamp
# may be in milliseconds, try `ts /= 1000` in that case
#print(datetime.utcfromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')) # 2018-12-23 06:29:05



timestamp_path = "/data/BGP_LOG/bitnodes_last_60days/timestamp_set.txt"

with open(timestamp_path) as f :
	content = f.readlines()
timestamp_list = [x.strip() for x in content]

per_day_superset_dict = dict()

for ts in timestamp_list :
	bitnodes_path = "/data/BGP_LOG/bitnodes_last_60days/port_removed/" + ts
	with open(bitnodes_path) as f :
		content = f.readlines()
	ip_list = [x.strip() for x in content]

	dt = datetime.utcfromtimestamp(int(ts)).strftime('%Y-%m-%d %H:%M:%S')
	dt = dt.split(' ')[0]
	dt_ymd = dt.split('-')[0] + dt.split('-')[1] + dt.split('-')[2]
	if(dt_ymd not in per_day_superset_dict.keys()) :
		per_day_superset_dict[dt_ymd] = set()
	for ip_addr in ip_list :
		per_day_superset_dict[dt_ymd].add(ip_addr)


result_path = "/data/BGP_LOG/bitnodes_last_60days/per_day_superset_of_btc_ipaddr/superset_"

for dt_ymd in per_day_superset_dict.keys() :
	print(dt_ymd)
	result = open(result_path + dt_ymd + ".txt", 'w')
	for ip_addr in per_day_superset_dict[dt_ymd] :
		result.write(ip_addr + '\n')