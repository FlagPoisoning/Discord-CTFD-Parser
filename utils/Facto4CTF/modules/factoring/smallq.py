import time
from modules.logger import logger,found_prime

from modules.utils import primes

def smallq(stop,n,timeout,args):
	try:
		for prime in primes(100000):
			if(stop.is_cancelled):
				return None
			elif n % prime == 0:
				q = prime
				p = n//q
				found_prime(p,q,stop,args,'smallq')
				return p,q
		return None
	except Exception as ex:
		logger('[+] Error: %s'%str(ex),'error',0,0)
