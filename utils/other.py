#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# _authors_: Vozec

import random
import os
import subprocess
import glob

from utils.logger import logger

def cleanpath(path):
    return os.path.relpath(os.path.normpath(os.path.join("/", path)), "/")

def findfile(name):
    found = []
    for file in glob.glob("./**/%s"%cleanpath(name), recursive = True):
        found.append(file)
    return found

def finddirectory(name):
    found = []
    for file in glob.glob("./**/%s"%(cleanpath(name)), recursive = True):
        found.append(file)
    return found


def rdnname():
	return str(random.randint(11111111,99999999))

def writefile(path,data):
	f = open(path, "a")
	f.write(data)
	f.close()
	
def readfile(path):
	f = open(path, "rb")
	cnt = f.read()
	f.close()
	return cnt


def sizeok(filename):
    # Check if Size is ok for Discord 

    if os.path.isfile(filename):
        size = os.path.getsize(filename)
        if int(size)//(1024*1024) > 7.50:
            return False
        else:
            return True
    else:
        return False

def b_filesize(l):

    # Convert file Lenght   
    units = ['B','kB','MB','GB','TB','PB']
    for k in range(len(units)):
        if l < (1024**(k+1)):
            break

    return "%4.2f %s" % (round(l/(1024**(k)),2), units[k])

def download(filename,path):
    try:
        # Try to curl > Save in file
        subprocess.run(["curl %s -o %s"%(filename,path)],shell=True,stderr=subprocess.PIPE,stdout=subprocess.PIPE,stdin=subprocess.PIPE)
        if(os.path.isfile(path)):
            return True
        else:
            return False
    except Exception as ex:
        logger(ex,'error',1,1)
        return False
