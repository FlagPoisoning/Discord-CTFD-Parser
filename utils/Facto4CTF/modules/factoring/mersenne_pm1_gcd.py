import time
from tqdm import tqdm
from modules.logger import logger,found_prime
from modules.utils import gcd,ilog2

def mersenne_pm1_gcd(stop,n,timeout,args):
    try:
        p = q = None
        for i in tqdm(range(2, ilog2(n)), disable=True):
            if(stop.is_cancelled):
                return None
            i2 = 2 ** i
            mersenne = [i2 - 1, i2 + 1]
            g0, g1 = gcd(mersenne[0], n), gcd(mersenne[1], n)
            if 1 < g0 < n:
                p = n // g0
                q = g0
                found_prime(p,q,stop,args,'mersenne_pm1_gcd')
                return p,q
            if 1 < g1 < n:
                p = n // g1
                q = g1
                found_prime(p,q,stop,args,'mersenne_pm1_gcd')
                return p,q
        return None
    except Exception as ex:
        logger('[+] Error: %s'%str(ex),'error',0,0)