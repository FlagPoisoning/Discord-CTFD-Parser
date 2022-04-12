import time
from modules.logger import logger,found_prime

from modules.utils import isqrt

def fermat(stop,n,timeout,args):
	try:
		a = b = isqrt(n)
		b2 = pow(a, 2) - n
		while pow(b, 2) != b2:
			if(stop.is_cancelled):
				return None
			a += 1
			b2 = pow(a, 2) - n
			b = isqrt(b2)
		p, q = (a + b), (a - b)
		assert n == p * q
		found_prime(p,q,stop,args,'fermat')
		return p,q
	except Exception as ex:
		logger('[+] Error: %s'%str(ex),'error',0,0)
