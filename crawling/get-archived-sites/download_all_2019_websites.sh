#!/bin/bash

# DOESNT WORK - USE THE PYTHON SCRIPT INSTEAD KING
# the reason it doesn't work is that spaces are included in the httrack cmd, and I don't know enough shell to stop it!

while read aurl; do
    echo "${aurl}"
    read domain
    echo $domain

    mkdir -p ${domain}
    
    httrack -O ${domain} ${aurl} -* +*/${domain}/*\
    -N1005\
    --depth=2\
    --advanced-progressinfo\
    --can-go-up-and-down\
    --display\
    --keep-alive\
    --mirror\
    --robots=0\
    --user-agent='Mozilla/5.0 (X11;U; Linux i686; en-GB; rv:1.9.1) Gecko/20090624 Ubuntu/9.04 (jaunty) Firefox/3.5'\
    --verbose

    echo "fin."

done <archived_sites.txt