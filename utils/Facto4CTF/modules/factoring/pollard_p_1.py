import time
from tqdm import tqdm
import math

from modules.logger import logger,found_prime
from modules.utils import gcd, isqrt, next_prime, primes, powmod

def pollard_p_1(stop,n,timeout,args):
	try:
		z = []
		logn = math.log(int(isqrt(n)))
		prime = primes(997)

		for j in range(0, len(prime)):
			primej = prime[j]
			logp = math.log(primej)
			for i in range(1, int(logn / logp) + 1):
				z.append(primej)
		for pp in tqdm(prime, disable=True):
			i = 0
			x = pp
			while True:
				if(stop.is_cancelled):
					return None
				x = powmod(x, z[i], n)
				i = i + 1
				y = gcd(n, x - 1)
				if y != 1:
					found_prime(y,n//y,stop,args,'pollard_p_1')
					return y,n//y
				if i >= len(z):
					return None


	except Exception as ex:
		logger('[+] Error: %s'%str(ex),'error',0,0)
