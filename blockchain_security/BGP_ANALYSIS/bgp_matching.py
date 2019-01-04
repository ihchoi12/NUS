import time

start = time.time()

bgp_announce_path =  './20180101'
bgp_information_path = './routeviews-rv2-20180101-1200.pfx2as'
bgp6_information_path = './routeviews-rv6-20180101-0800.pfx2as'
#bgp_announce_path =  './A.txt'
#bgp_information_path = './B.txt'

write_path = './result_test.txt'
write_result = open(write_path, 'w')


bgp_information_set = set()
bgp_information = open(bgp_information_path, 'r')
while(True):
	new_line = bgp_information.readline()
	if(new_line == ''):
		break
	line_list = new_line.split('\t')
	info_string = line_list[0] + '/' + line_list[1] + ':' + line_list[2]
	bgp_information_set.add(info_string)


bgp6_information_set = set()
bgp6_information = open(bgp6_information_path, 'r')
while(True):
	new_line = bgp6_information.readline()
	if(new_line == ''):
		break
	line_list = new_line.split('\t')
	info_string = line_list[0] + '/' + line_list[1] + ':' + line_list[2]
	bgp6_information_set.add(info_string)





bgp_announce = open(bgp_announce_path, 'r')
while(True):
	new_line = bgp_announce.readline()
	if(new_line == ''):
		break
	line_list = new_line.split(' ')
	info_string = line_list[1] + ':' + line_list[3]
	if(info_string not in bgp_information_set and info_string not in bgp6_information_set):
		write_result.write(new_line)

write_result.close()
#print(bgp_announce_set)

end = time.time()
print(end - start)