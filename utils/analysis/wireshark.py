#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# _authors_: Vozec


import os
import random
from scapy.all import *
import pcapkit
import binascii
import subprocess

from utils.other import rdnname,writefile

def execmd(cmd):
	cnt = subprocess.Popen(cmd,shell=True,stderr=subprocess.PIPE,stdout=subprocess.PIPE,stdin=subprocess.PIPE).communicate()[0].decode()
	return cnt

def append(result,command,cnt):
    if len(cnt) < 2000  and 'strings' != command.lower():
        result.append('**%s**```\n%s```'%(command,cnt))
    else:
        rdn_name = rdnname()
        writefile('/tmp/%s.txt'%str(rdn_name),cnt)
        result.append(['**%s**'%command,'/tmp/%s.txt'%str(rdn_name)])
    return result

def analyse_wireshark(path_document,ext,formatflag):

	result = []

	# General Commands
	cmd = {
		"Strings":"timeout 10 strings -t x %s"%path_document,
		"Strings_head":"timeout 10 strings -t x %s | head -n 20"%path_document,
		"Strings_bottom":"timeout 10 strings -t x %s | tail -n 20"%path_document,
		"Strings Flag Grepped":"timeout 10 strings -t x %s | grep \"{formatflag}\""%path_document,	
		"Binwalk":"timeout 10 binwalk %s"%path_document,
		"SslDump":"timeout 10 ssldump -r %s"%path_document,
		"Tshark Meta-Data":"tshark -r %s -q -z http,tree"%path_document,
		"Tshark HTTP":"tshark -r %s -Y http.request -T fields -e http.host -e http.user_agent"%path_document
		}

	for command in cmd.keys():
		try:
			cnt = execmd(cmd[command])
			result = append(result,command,cnt)			
		except Exception as ex:
			result.append('**%s**```\n%s```'%(command,str(ex)))



	# PcapKit cmd
	try:
		rdn_name = rdnname()
		plist = pcapkit.extract(fin=path_document, fout='/tmp/%s.json'%rdn_name, format='json', store=False)
		result.append(['**PcapKit**','/tmp/%s.json'%rdn_name])
	except Exception as ex:
		result.append('**PcapKit**```\n%s```'%(str(ex)))


	# ChaosReader Analyse
	namefile = rdnname()
	chaos_cmd = 'mkdir -p /tmp/%s;cd /tmp/%s;chaosreader %s;zip -q -r /tmp/%s.zip /tmp/%s echo /tmp/%s.zip;rm -r /tmp/%s'%(namefile,namefile,path_document,namefile,namefile,namefile,namefile);
	try:
		res = execmd(chaos_cmd)		
		if(os.path.isfile('/tmp/%s.zip'%namefile)):
			result.append(['**ChaosReader**','/tmp/%s.zip'%namefile])
	except Exception as ex:
		result.append('**ChaosReader**```\n%s```'%(str(ex)))


	# RdpCap
	packets = rdpcap(path_document)
	all_ = []
	for p in packets:
		try:
			all_.append(p[Raw].load)
		except:
			pass
	rdn_name = rdnname()
	writefile('/tmp/%s.txt'%rdn_name,str(all_))
	result.append(['**RdpCap_Data**','/tmp/%s.txt'%rdn_name])
 
	
	
	# RdpCap unhexlified
	all_hex = ''
	for p in all_:
		try:
			all_hex += str(binascii.unhexlify(p))+'\n'
		except:
			pass				
	rdn_name = rdnname()
	writefile('/tmp/%s.txt'%rdn_name,str(all_hex))
	result.append(['**RdpCap_Data_Unhexlified**','/tmp/%s.txt'%rdn_name])


	# Udp packets to files
	rdn_name = rdnname()
	with open('/tmp/%s.raw'%rdn_name, 'wb') as f:
		for p in packets:
			if UDP in p:
				try:
					chunk = bytes(p[Raw])
					f.write(chunk)
				except:
					pass
	result.append(['**UDP Data Dumped**','/tmp/%s.raw',rdn_name])


	# File on the Raw file
	path = '/tmp/%s.raw'%rdn_name
	if(os.path.isfile(path) and os.path.getsize(path) > 0):
		cnt = os.popen('file /tmp/%s.raw'%rdn_name).read()
		result.append('**File on %s.raw**```\n%s```'%(rdn_name,cnt))

	
	return result