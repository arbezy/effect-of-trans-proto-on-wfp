import sys
from selenium import webdriver
from time import sleep

from dumputils import *
from common import *
from utils import *

# If crawling a caddy server hosted in a separate docker container, will need to install root certificates from the caddy server into chrome browser

# args should be ?(self?), visit_number, url_visited 
i, url = sys.argv[1:3]
print(f'Visit {i} to {url}')
    
coptions = webdriver.ChromeOptions()

#coptions.add_argument('--no-proxy-server')
#coptions.add_argument('--no-sandbox')
#coptions.add_argument('--ignore-certificate-errors')
#coptions.add_experimental_option('excludeSwitches', ['enable-logging'])

coptions.add_argument('--user-data-dir=/home/seluser/.config/google-chrome')

# NOTE: also included in the actual version is flags to set the cache size to 1

coptions.add_argument('--disable-gpu')
coptions.add_argument('--enable-quic')
coptions.add_argument('--origin-to-force-quic-on=host.docker.internal:2020')

#with webdriver.Remote("http://localhost:4444", options=coptions) as driver:
with webdriver.Chrome(options=coptions) as driver:
    sleep(2)
    site = url.split('//')[1].split('.')[0]
    fname = f'/usr/src/app/results/{i}_{site}.pcap'
    with Sniffer(path=fname, filter=DEFAULT_UDP_FILTER):
        driver.get(url)
        driver.save_screenshot(filename=f'/usr/src/app/screenshots/screenie_{i}_{site}.png')
        sleep(5)
