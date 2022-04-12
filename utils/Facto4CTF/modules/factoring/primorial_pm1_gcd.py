import time
from tqdm import tqdm
from modules.logger import logger,found_prime
from modules.utils import gcd,next_prime

def primorial_pm1_gcd(stop,n,timeout,args):
	try:
		limit = 100000
		prime = 1
		primorial = 1
		p = q = None
		for x in tqdm(range(0, limit), disable=True):
			if(stop.is_cancelled):
				return None
			prime = next_prime(prime)
			primorial *= prime
			primorial_p1 = [primorial - 1, primorial + 1]
			g0, g1 = gcd(primorial_p1[0], n), gcd(primorial_p1[1], n)
			if 1 < g0 < n:
				p = n // g0
				q = g0
				found_prime(p,q,stop,args,'primorial_pm1_gcd')
				return p,q
			if 1 < g1 < n:
				p = n // g1
				q = g1
				found_prime(p,q,stop,args,'primorial_pm1_gcd')
				return p,q
		return None
	except Exception as ex:
		logger('[+] Error: %s'%str(ex),'error',0,0)