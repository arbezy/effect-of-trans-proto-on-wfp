# Python program to check whether a website was successfully crawled.

import os
import sys

pcap_filenames = []
pcap_filesizes = []

for f in os.listdir(sys.argv[1]):
    filepath = os.path.join(sys.argv[1], f)
    if f.endswith('.pcap'):
        pcap_filenames.append(f)
        pcap_size = os.path.getsize(filepath)
        if pcap_size < 1000:
            print(f"{f} is smaller than 10 KB, suspicious")
        pcap_filesizes.append(pcap_size)
        
filesize_zipped = list(zip(pcap_filenames, pcap_filesizes))
print(filesize_zipped)



