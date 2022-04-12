import time
from modules.logger import logger,found_prime
from tqdm import tqdm
from modules.utils import getpubkeysz

def mersene_prime(stop,n,timeout,args):
	try:
		p = q = None
		mersenne_tab = [2,3,5,7,13,17,19,31,61,89,107,127,521,607,1279,2203,2281,3217,4253,4423,9689,9941,11213,19937,21701,23209,44497,86243,110503,132049,216091,756839,859433,1257787,1398269,2976221,3021377,6972593,13466917,20336011,24036583,25964951,30402457,32582657,37156667,42643801,43112609,57885161,74207281,77232917,82589933,]
		i = getpubkeysz(n)
		for mersenne_prime in tqdm(mersenne_tab, disable=True):
			if(stop.is_cancelled):
				return None
			if mersenne_prime <= i:
				m = (1 << mersenne_prime) - 1
				if n % m == 0:
					p = m
					q = n // p
					found_prime(p,q,stop,args,'mersenne_prime')
					return p,q
			else:
				return None
		return None
	except Exception as ex:
		logger('[+] Error: %s'%str(ex),'error',0,0)
