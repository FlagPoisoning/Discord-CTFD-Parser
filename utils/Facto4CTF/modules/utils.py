import random
import gmpy2 as gmpy
import math
import subprocess

def kill_sage():
    subprocess.run("ps -aux | grep sage | grep -v grep | awk '{print $2}' | xargs -r kill -9",shell=True,stderr=subprocess.DEVNULL,stdout=subprocess.DEVNULL,stdin=subprocess.DEVNULL)
    
def getpubkeysz(n):
    size = int(math.log2(n))
    if size & 1 != 0:
        size += 1
    return size


def gcd(a, b):
    while b:
        a, b = b, a % b
    return abs(a)

def _primes_yield_gmpy(n):
    p = i = 1
    while i <= n:
        p = gmpy.next_prime(p)
        yield p
        i += 1

def _primes_gmpy(n):
    return list(_primes_yield_gmpy(n))



def isqrt(n):
    if n == 0:
        return 0
    x, y = n, (n + 1) >> 1
    while y < x:
        x, y = y, (y + n // y) >> 1
    return x


def fermat_prime_criterion(n, b=2):
    return pow(b, n - 1, n) == 1


def is_prime(n):
    if (
        fermat_prime_criterion(n)
        and fermat_prime_criterion(n, b=3)
        and fermat_prime_criterion(n, b=5)
    ):
        return miller_rabin(n)
    else:
        return False

def miller_rabin(n, k=40):
    if n == 2:
        return True

    if n & 1 == 0:
        return False

    r, s = 0, n - 1
    while s & 1 == 0:
        r += 1
        s >>= 1
    i = 0
    for i in range(0, k):
        a = random.randrange(2, n - 1)
        x = pow(a, s, n)
        if x == 1 or x == n - 1:
            continue
        j = 0
        while j <= r - 1:
            x = pow(x, 2, n)
            if x == n - 1:
                break
            j += 1
        else:
            return False
    return True

def fib(n):
    a, b = 0, 1
    i = 0
    while i <= n:
        a, b = b, a + b
        i += 1
    return a

def next_prime(n):
    while True:
        if is_prime(n):
            return n
        n += 1

def _ilog2_gmpy(n):
    return int(gmpy.log2(n))

powmod = gmpy.powmod
primes = _primes_gmpy
ilog2 = _ilog2_gmpy