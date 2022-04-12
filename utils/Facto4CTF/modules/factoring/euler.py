import time
from tqdm import tqdm
from modules.logger import logger,found_prime
from modules.utils import isqrt,gcd

def euler(stop,n,timeout,args):
	try:
		if (n - 1) % 4 != 0:
			return None

		if n & 1 == 0:
			return (n >> 1, 2) if n > 2 else (2, 1)
		end = isqrt(n)
		a = 0
		solutionsFound = []
		firstb = -1

		while a < end and len(solutionsFound) < 2:
			if(stop.is_cancelled):
				return None
			bsquare = n - pow(a, 2)
			if bsquare > 0:
				b = isqrt(bsquare)
				if (pow(b, 2) == bsquare) and (a != firstb) and (b != firstb):
					firstb = b
					solutionsFound.append([b, a])
			a += 1
		if len(solutionsFound) < 2:
			return None

		a = solutionsFound[0][0]
		b = solutionsFound[0][1]
		c = solutionsFound[1][0]
		d = solutionsFound[1][1]

		k = pow(gcd(a - c, d - b), 2)
		h = pow(gcd(a + c, d + b), 2)
		m = pow(gcd(a + c, d - b), 2)
		l = pow(gcd(a - c, d + b), 2)

		p, q = gcd(k + h, n), gcd(l + m, n)

		if n > p > 1:
			found_prime(p,n // p,stop,args,'euler')
			return p,n // p

		if n > q > 1:
			found_prime(q,n // q,stop,args,'euler')
			return q,n // q

		return None
	except Exception as ex:
		logger('[+] Error: %s'%str(ex),'error',0,0)