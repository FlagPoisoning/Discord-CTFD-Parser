import time
from modules.logger import logger
import random

from modules.utils import is_prime,gcd

def pollard_rho(stop,n,timeout,args, seed=2, p=2, c=1):
	try:
		if n & 1 == 0:
			return 2
		if n % 3 == 0:
			return 3
		if n % 5 == 0:
			return 5
		if is_prime(n):
			return n
		f = lambda x: x ** p + c
		x, y = seed, seed
		while True:
			if(stop.is_cancelled):
				return None
			x = f(x) % n
			y = f(f(y)) % n
			d = gcd((x - y), n)
			if d > 1:
				found_prime(d,n//d,stop,args,'pollard_rho')				
				return d,n//d
	except Exception as ex:
		logger('[+] Error: %s'%str(ex),'error',0,0)