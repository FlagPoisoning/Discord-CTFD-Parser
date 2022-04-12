import os
import subprocess
import r2pipe
from utils.other import rdnname,writefile

def execmd(cmd):
	cnt = b''.join(subprocess.Popen(cmd,shell=True,stderr=subprocess.PIPE,stdout=subprocess.PIPE,stdin=subprocess.PIPE).communicate()).decode()
	return cnt

def append(result,command,cnt):
    if len(cnt) < 2000  and 'strings' != command.lower():
        result.append('**%s**```\n%s```'%(command,cnt))
    else:
        rdn_name = rdnname()
        writefile('/tmp/%s.txt'%str(rdn_name),cnt)
        result.append(['**%s**'%command,'/tmp/%s.txt'%str(rdn_name)]) 
    return result

def rad2(file):
	r = r2pipe.open(file)
	final  = '-'*30+'\n'
	final += r.cmd('aaa;afl')
	final += '-'*30+'\n'
	final += r.cmd("iz")
	final += '-'*30+'\n'	
	return final

def rad2_getmain(file):
	r = r2pipe.open(file)
	final = '-'*30+'\n'
	r.cmd("aaa;af")
	final += r.cmd("pdf @main")
	final += '-'*30+'\n'
	return final


def analyse_elf(file,ext):
	result = []

	cmd = {
		"Strings":"timeout 10 strings %s"%file,
		"File":"timeout 10 file %s"%file,
		"Checksec":"timeout 10 checksec %s"%file,
		"Header":"timeout 10 readelf -h  %s"%file,
		"Header Section":"timeout 10 readelf -S  %s"%file,
		"Strace":"timeout 10 echo 'guess' | strace %s guess2"%file,
		"Ltrace":"timeout 10 echo 'guess' | ltrace %s guess2"%file,		
	}

	for command in cmd.keys():
		try:
			cnt = execmd(cmd[command])
			result = append(result,command,cnt)
		except Exception as ex:
			result.append('**%s**```\n%s```'%(command,str(ex)))

	try:
		cnt = rad2(file)
		result = append(result,"Radare2",cnt)
	except Exception as ex:
		result.append('**Radare2**```\n%s```'%str(ex))

	try:
		cnt = rad2_getmain(file)
		result = append(result,"Radare2 Main",cnt)
	except Exception as ex:
		result.append('**Radare2 Main**```\n%s```'%str(ex))

	return result