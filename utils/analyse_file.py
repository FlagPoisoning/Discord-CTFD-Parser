#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# _authors_: Vozec

import os
import random
import time
import re
import sys

from utils.logger import logger
from utils.other import readfile


from utils.analysis.image import analyse_picture
from utils.analysis.sound import analyse_sound
from utils.analysis.openssl import analyse_key
from utils.analysis.document import analyse_document
from utils.analysis.wireshark import analyse_wireshark
from utils.analysis.elf import analyse_elf


def b_filesize(l):
	units = ['B','kB','MB','GB','TB','PB']
	for k in range(len(units)):
		if l < (1024**(k+1)):
			break
	return "%4.2f %s" % (round(l/(1024**(k)),2), units[k])

def search4flag(result,formatflag):

	# Search for flag
	found = []

	for element in result:
		try:
			if type(element) == list and '.txt' in element[1] :
				for flag in re.findall(formatflag+r'{(.*?)}',str(readfile(element[1]))):
					found.append('%s{%s}'%(formatflag,flag))

			elif type(element) == str:
				for flag in re.findall(formatflag+r'{(.*?)}',element):
					found.append('%s{%s}'%(formatflag,flag))

		except Exception as ex:
			logger('%s > %s'%(str(ex),element[:20]),'error',1,1)
	return found

def analysis(pathfile,formatflag):

	final = []
	embed = ''

	file = os.path.basename(pathfile)
	file_cmd = os.popen('file "%s"'%pathfile).read().split(pathfile)[1]
	size = b_filesize(int(os.path.getsize(pathfile)))
	line = os.popen('xxd -p -l 12 "%s"'%pathfile).read()

	magic = ''.join([line[i:i+2]+' ' for i in range(0, len(line), 2)])

	embed += "__Type__ %s"%file_cmd
	embed += "__Size__ %s\n"%size
	embed += "__MagicBytes__ %s\n"%magic

	ext_image = ['.png','.jpg','.jpeg','.gif','.bmp'] 
	ext_sound = ['.wav','.mp3','.ogg']
	ext_document = ['.docx','.pdf','.txt','.odt','.doc','.docm']
	ext_key = ['.pub','.pem']
	ext_wireshark = ['.pcap','.pcapng','.cap']

	header_document = ["ASCII text"]

	ext = os.path.splitext(pathfile)[1]	 

	if(ext in ext_image):
		final+= analyse_picture(pathfile,ext)

	elif (ext in ext_sound):
		final+= analyse_sound(pathfile,ext)

	elif (ext in ext_wireshark):
		final += analyse_wireshark(pathfile,ext,formatflag)

	elif (ext in ext_key):
		final += analyse_key(pathfile,ext)

	elif (ext in ext_document or ext[:3] == 'doc'):
		final += analyse_document(pathfile,ext)

	elif ('ELF' in file_cmd):
		final += analyse_elf(pathfile,ext)

	else:
		for head in header_document:
			if head in header_document:
				final += analyse_document(pathfile,ext)

	if final == []:
		final += ["**[+] Extension not supported: %s**"%ext]


	return final,embed,search4flag(final,formatflag)
