import requests
from bs4 import BeautifulSoup
import re
import time
import sys

url_base = 'http://ipinfo.io/'
as_base = 'AS'

i_start = int(sys.argv[1])
i_end = int(sys.argv[2])

output1 = open('ip_per_asn_ipinfo/addition-'+str(i_start)+'-'+str(i_end)+'.csv', 'w')
output2 = open('peer_per_asn_ipinfo/addition-'+str(i_start)+'-'+str(i_end)+'.csv', 'w')
with open('asn-addition.txt') as f:
    lines = f.read().splitlines()
    for i in range(i_start, i_end):
        asn = lines[i]
        ASN = as_base + asn
        page = requests.get(url_base+ASN)
        html_doc = page.content
        soup = BeautifulSoup(html_doc, 'html.parser')
        for link in soup.find_all('a'):
            # print link
            if ASN in link.get('href'):
                auxstring = '/'+as_base+asn+'/'
                line = re.sub(auxstring, '', link.get('href'))
                printstring = asn+','+line+'\n'
                if 'AS' not in printstring:
                    output1.write(printstring)
            if asn not in link.get('href') and "AS" in link.get('href'):
                # print asn, link
                auxstring = '/'+as_base+asn+'/'
                line = re.sub(auxstring, '', link.get('href'))
                line1 = line.replace('/AS','')
                printstring = asn+','+line1+'\n'
                if 'AS' not in printstring:
                    output2.write(printstring)
        time.sleep(2)

print str(i_start)+'-'+str(i_end)+' script finished'
