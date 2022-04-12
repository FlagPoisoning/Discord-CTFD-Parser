import time
from tqdm import tqdm

from modules.logger import logger,found_prime
from modules.utils import gcd

def fermat_numbers_gcd(stop,n,timeout,args):
	try:
		limit = 10000
		p = q = None
		for x in tqdm(range(1, limit), disable=True):
			if(stop.is_cancelled):
				return None
			f = (2 ** 2 ** x) + 1
			fermat = gcd(f, n)
			if 1 < fermat < n:
				p = n // fermat
				q = fermat
				found_prime(p,q,stop,args,'fermat_numbers_gcd')
				return p,q
		return None
	except Exception as ex:
		logger('[+] Error: %s'%str(ex),'error',0,0)