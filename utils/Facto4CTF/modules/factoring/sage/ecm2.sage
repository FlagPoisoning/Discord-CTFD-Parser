#!/usr/bin/env sage

import sys

try:
    print(ecm.factor(int(sys.argv[1]))[0])    
except:
    print(1)