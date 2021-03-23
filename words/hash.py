import hashlib, binascii
import sys
with open(sys.argv[1], "r",encoding="utf-8") as f:
    temp = f.read().splitlines()
    for each_elem in temp:
        global res
        res = hashlib.new('md4', each_elem.encode('utf-16le')).digest()
        res = (binascii.hexlify(res).decode('utf-8'))
        print(res)
