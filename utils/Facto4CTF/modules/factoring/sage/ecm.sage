#!/usr/bin/env sage

import sys

try:
    print(ecm.find_factor(int(sys.argv[1]))[0])    
except:
    print(1)