import os
from subprocess import Popen , PIPE
from time import sleep
from factordb.factordb import FactorDB
import json

def execmd(cmd,t):
	cnt = Popen(cmd,shell=True,stderr=PIPE,stdout=PIPE,stdin=PIPE)
	for k in range((t*60)):
		sleep(1)
		if(cnt.poll() is not None):
			return cnt.communicate()[0].decode()
	cnt.kill()
	return None

def factordb_search(n):
	try:
		f = FactorDB(n)
		f.connect()
		res = f.get_factor_list()
		return res		
	except Exception as ex:
		return None

def facto(n,timeout):
	try:
		facto4ctf_path = os.path.dirname(os.path.abspath(__file__))+'/Facto4CTF/facto4ctf.py'
		resp = factordb_search(n)
		
		if(len(resp) == 1 or resp == None):
			cmd = 'python3 %s -n %s -t %s -a -j -q'%(facto4ctf_path,str(n),str(timeout))
			resp2 = execmd(cmd,timeout).strip()
			if(resp2 != ''):
				json_load = json.loads(resp2)
				if(len(json_load["factor"]) == 2 ):
					return '**[+] 2 Factors Found : **\n```P=%s\nQ=%s```'%(json_load["factor"][0],json_load["factor"][1])
				else:
					return '**[+] %s Factors Found : **\n```%s```'%(str(len(json_load["factor"])),str(json_load["factor"]))
			else:
				return None
		elif len(resp) == 2:
			return '**[+] 2 Factors Found : **\n```P=%s\nQ=%s```'%(str(resp[0]),str(resp[1]))
		else:
			return '**[+] %s Factors Found : **\n```%s```'%(str(len(resp)),str(resp))

	except Exception as ex:
		print(ex)
		return 'Error : ```%s```'%str(ex)