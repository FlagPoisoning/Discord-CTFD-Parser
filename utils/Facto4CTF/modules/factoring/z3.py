import time
import multiprocessing

from modules.logger import logger,found_prime
from z3 import Solver, Int, set_param, sat
from modules.utils import isqrt,next_prime

def z3(stop,n,timeout,args):
	t1 = multiprocessing.Process(target =run, args =(stop,n,timeout,args))
	t1.start()
	while(True):
		if(stop.is_cancelled):
			t1.terminate()
			return None
		if not t1.is_alive():
			return None		
		time.sleep(1.5)

def run(stop,n,timeout,args):
	try:
		s = Solver()
		s.set("timeout", timeout * 1000)
		p = Int("p")
		q = Int("q")
		i = int(isqrt(n))
		np = int(next_prime(i))
		s.add(
			p * q == n,
			n > p,
			n > q,
			p >= np,
			q < i,
			q > 1,
			p > 1,
			q % 2 != 0,
			p % 2 != 0,
		)
		s_check_output = s.check()
		if s_check_output == sat:
			res = s.model()
			p, q= res[p].as_long(), res[q].as_long()
			assert p * q == n
			found_prime(p,q,stop,args,'z3')
			return p,q			
		else:
			return None
	except Exception as ex:
		logger('[+] Error: %s'%str(ex),'error',0,0)

