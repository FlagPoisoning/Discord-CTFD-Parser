import time
from tqdm import tqdm
import math

from modules.logger import logger,found_prime

from modules.utils import isqrt,powmod,fib,gcd

def fibonacci_gcd(stop,n,timeout,args):
	try:
		limit = 10000
		p = q = None
		for x in tqdm(range(1, limit), disable=True):
			if(stop.is_cancelled):
				return None
			f = gcd(fib(x), n)
			if 1 < f < n:
				p = n // f
				q = f
				found_prime(p,q,stop,args,'fibonacci_gcd')
				return p,q
		return None

	except Exception as ex:
		logger('[+] Error: %s'%str(ex),'error',0,0)
