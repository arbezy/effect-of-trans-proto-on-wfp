import os
import sys
from time import sleep

# created for a windows machine with bash & httrack installed and added to system environment vars

# TODO: remove uses of first_line (deprecated)
# TODO: complete archived_site.txt with all websites

with open('C:/Users/andre/Uni_Documents/Dissertation/archived_websites/archived_sites.txt') as fp:
    first_line = True
    i=0
    for line in fp:
        # archive url and domain seperated by a space in archived_sites file
        line = line.split(' ')
        domain = line[1]
        # archive urls obtained from wayback machine
        aurl = line[0]
        
        print(f"\n NOTE: mirroring {domain} from {aurl} \n")
        
        # TODO: check this only downloads resources from the same origin -> I'm not sure it does...
        
        if first_line:
            # initialises httrack project, using the first website
            # cannot init when using the --continue flag so it is excluded.
            os.system(f"httrack {aurl} -O1 results/{i} -* +*/{domain}/*"
            " -N1005 --depth=2 --advanced-progressinfo --can-go-up-and-down"
            " --display --keep-alive --mirror --robots=0"
            " --user-agent='Mozilla/5.0 (X11;U; Linux i686; en-GB; rv:1.9.1) Gecko/20090624 Ubuntu/9.04 (jaunty) Firefox/3.5' --verbose")
        else:
            print("continuing...")
            # called with --continue to add to existing project
            os.system(f"httrack {aurl} -O1 results/{i} -* +*/{domain}/*"
            " -N1005 --depth=2 --advanced-progressinfo --can-go-up-and-down"
            " --display --keep-alive --mirror --robots=0 --continue"
            " --user-agent='Mozilla/5.0 (X11;U; Linux i686; en-GB; rv:1.9.1) Gecko/20090624 Ubuntu/9.04 (jaunty) Firefox/3.5' --verbose")
        
        first_line = False
        i+=1

sleep(1)
os.system("bash -c cd results")
sleep(2)
os.system("bash -c tree -H '.' -L 1 --noreport --dirsfirst --charset utf-8 -I 'index.html' -o index.html")
sleep(2)