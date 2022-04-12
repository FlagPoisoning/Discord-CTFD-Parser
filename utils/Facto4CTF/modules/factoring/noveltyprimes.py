import time
from tqdm import tqdm
from modules.logger import logger,found_prime

def noveltyprimes(stop,n,timeout,args):
	try:
		maxlen = 25
		for i in tqdm(range(maxlen - 4), disable=True):
			if(stop.is_cancelled):
				return None
			prime = int("3133" + ("3" * i) + "7")
			if(n%prime == 0):
				p = prime
				q = n // p
				found_prime(p,q,stop,args,'primorial_pm1_gcd')
				return p,q
		return None
	except Exception as ex:
		logger('[+] Error: %s'%str(ex),'error',0,0)