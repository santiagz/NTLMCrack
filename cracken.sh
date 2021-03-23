#!/bin/bash
#hashcat -a 3 -m 0 sss.hash /usr/share/wordlists/rock_500.txt -O -o cracked.txt --potfile-disable
if [[ "$1" == "cat_win" ]]; then
  hashcat --force --hwmon-temp-abort=100 -m 1000 -D 1,2 -a 0 $2 words/all.txt -O -o $3
  hashcat --force --hwmon-temp-abort=100 -m 1000 -D 1,2 -a 0 $2 words/all.txt -O -o $3 --show
elif [[ "$1" == "john_tg" ]]; then
  john-bleeding-jumbo/run/john $2 --wordlist=words/onefile.txt
  john-bleeding-jumbo/run/john $2 --show >> $3
else
  echo "Something wrong!"
fi

