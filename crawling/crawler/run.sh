#!/bin/bash

VISITS=10

rm -rf results
mkdir -p results
rm -rf screenshots
mkdir screenshots

echo "removed previous results"


while read url; do
	for i in {0..9}; do
        python3 main.py $i https://$url
		# I think these kill lines are unecessary? as dumpcap killed elsewhere at least
		killall -9 dumpcap
		killall -9 python3
    done 
done <urls.txt
