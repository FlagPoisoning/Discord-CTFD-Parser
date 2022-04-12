import time
from random import randint
from tqdm import tqdm
from modules.logger import logger,found_prime
from modules.utils import gcd,powmod

def brent(stop,n,timeout,args):
	try:
		poll_res = run(stop,n,timeout,args)
		if(poll_res != None):
			p = poll_res
			q = n//poll_res
			found_prime(p,q,stop,args,'brent')
			return p,q
		else:
			return None

	except Exception as ex:
		logger('[+] Error: %s'%str(ex),'error',0,0)

def run(stop,N,timeout,args):
	if N & 1 == 0:
		return 2
	g = N
	while g == N:
		if(stop.is_cancelled):
			return None
		y, c, m = randint(1, N - 1), randint(1, N - 1), randint(1, N - 1)
		g, r, q = 1, 1, 1
		while g == 1:
			if(stop.is_cancelled):
				return None
			x = y
			i = 0
			while i <= r:
				if(stop.is_cancelled):
					return None
				y = (powmod(y, 2, N) + c) % N
				i += 1
			k = 0
			while k < r and g == 1:
				if(stop.is_cancelled):
					return None
				ys = y
				i = 0
				while i <= min(m, r - k):
					if(stop.is_cancelled):
						return None
					y = (powmod(y, 2, N) + c) % N
					q = q * (abs(x - y)) % N
					i += 1
				g, k = gcd(q, N), k + m
				if N > g > 1:
					return g
			r <<= 1
		if g == N:
			while True:
				if(stop.is_cancelled):
					return None
				ys = (powmod(ys, 2, N) + c) % N
				g = gcd(abs(x - ys), N)
				if N > g > 1:
					return g