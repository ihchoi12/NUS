from scapy.all import rdpcap
from scapy.all import wrpcap

packet_list = rdpcap('/home/ihchoi/NUS/NUS/blockchain_security/version_handling/real_packet.pcap')

print len(packet_list)

print packet_list[18].show()
'''
packet_list[0]['TCP'].sport = 1235
#print packet_list[0]['IP'].dst
packet_list[0]['IP'].src = '10.0.0.2'
packet_list[0]['IP'].dst = '10.0.0.1'
#print packet_list[0]['IP'].dst
print packet_list[0].show()
'''
wrpcap("modified_real_version.pcap", packet_list[18])
