import os
import random
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

def analyse_key(path_document,ext):
	result = []

	cmd = {
		"OpenSsl PublicKey":"timeout 10 openssl rsa -noout -text -inform PEM -in '%s' -pubin -modulus"%path_document,
		"OpenSsl PrivateKey":"timeout 10 openssl rsa -noout -text -in '%s' -modulus"%path_document,		
		}

	for command in cmd.keys():
		try:
			cnt = execmd(cmd[command])
			result = append(result,command,cnt)
		except Exception as ex:
			result.append('**%s**```\n%s```'%(command,str(ex)))


	return result