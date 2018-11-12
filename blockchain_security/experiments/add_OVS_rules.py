import os


out = open("./"+ "OVSrules" +".txt", "w")


def add_arp_rules() :
	out.write("sudo ovs-ofctl add-flow br0 \"arp,in_port=1,arp_spa=10.0.0.1,arp_tpa=10.0.0.2 actions=output:2\"" + '\n')
	out.write("sudo ovs-ofctl add-flow br0 \"arp,in_port=2,arp_spa=10.0.0.2,arp_tpa=10.0.0.1 actions=output:1\"" + '\n')

def add_icmp_rules() :
	out.write(
		"sudo ovs-ofctl add-flow br0 \"icmp,in_port=1,dl_src=08:00:27:2a:87:c3,dl_dst=08:00:27:f3:68:2a,nw_src=10.0.0.1,nw_dst=10.0.0.2, actions=output:2\""
		 + '\n')
	out.write(
		"sudo ovs-ofctl add-flow br0 \"icmp,in_port=2,dl_src=08:00:27:f3:68:2a,dl_dst=08:00:27:2a:87:c3,nw_src=10.0.0.2,nw_dst=10.0.0.1, actions=output:1\""
		 + '\n')


def add_tcp_rules() :
	path_dir = './attack_resource/'
	file_list = os.listdir(path_dir)
	port = 49152
	print(file_list)
	
	for sender in file_list :
		sender = sender[0:len(sender)-4]
		
		out.write(
			"sudo ovs-ofctl add-flow br0 \"tcp,in_port=2,dl_src=08:00:27:f3:68:2a,dl_dst=08:00:27:2a:87:c3,nw_src=10.0.0.2," + 
			"tp_src="+ str(port) +",nw_dst=10.0.0.1 actions=mod_nw_src:" + sender + ",output:1\"" + '\n')
		out.write(
			"sudo ovs-ofctl add-flow br0 \"tcp,in_port=1,dl_src=08:00:27:2a:87:c3,dl_dst=08:00:27:f3:68:2a,nw_src=10.0.0.1," + 
			"tp_dst="+ str(port) +",nw_dst=" + sender + " actions=mod_nw_dst:10.0.0.2,output:2\"" + '\n')

		port += 1
		

add_arp_rules()
add_icmp_rules()
add_tcp_rules()
