import os
import random
import pyUnicodeSteganography as usteg
import subprocess
from utils.other import rdnname,writefile,readfile

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

def analyse_document(path_document,ext):
	result = []

	cmd = {
		"Strings":"timeout 10 strings -t x %s"%path_document,
		"Strings_head":"timeout 10 strings -t x %s | head -n 20"%path_document,
		"Strings_bottom":"timeout 10 strings -t x %s | tail -n 20"%path_document,
		"Binwalk":"timeout 10 binwalk %s"%path_document,
		"StegSnow":"timeout 10 stegsnow -C %s"%path_document
		}


	# Commande classique   
	for command in cmd.keys():
		try:
			cnt = execmd(cmd[command])
			result = append(result,command,cnt)
		except Exception as ex:
			result.append('**%s**```\n%s```'%(command,str(ex)))



	# If Word document > Extract Macro	
	olevba_cmd = "timeout 10 olevba %s --decode"%path_document

	if(ext in ['.docx','.odt','.doc','.docm']):
		try:
			cnt = execmd(olevba_cmd)
			result = append(result,"Olevba",cnt)
		except Exception as ex:
			result.append('**Olevba**```\n%s```'%str(ex))
	


	# If it's Text document > usteg
	if(ext in ['.txt','']):
		try:
			encoded = readfile(path_document)
			cnt = usteg.decode(encoded)
			if(cnt != ''):
				result = append(result,"ZWSP",cnt)
		except Exception as ex:
			result.append('**ZWSP**```\n%s```'%str(ex))

	if(ext in ['.pdf']):
		try:
			cmd = 'timeout 10 pdf-parser %s'%path_document
			cnt = execmd(cmd)
			result = append(result,"Pdf Parser",cnt)
		except Exception as ex:
			result.append('**Pdf Parser**```\n%s```'%str(ex))



	return result