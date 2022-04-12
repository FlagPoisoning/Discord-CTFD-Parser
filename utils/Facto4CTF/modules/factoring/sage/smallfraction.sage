#!/usr/bin/env sage

import sys


def factor(n):
    depth = 50
    x = PolynomialRing(Zmod(n), "x").gen()

    for den in IntegerRange(2, depth + 1):
        for num in IntegerRange(1, den):
            if gcd(num, den) == 1:
                r = den / num
                phint = isqrt(n * r)
                f = x - phint
                sr = f.small_roots(beta=0.5)

                if len(sr) > 0:
                    p = phint - sr[0]
                    p = p.lift()
                    if n % p == 0:
                        return p


try:
    n = int(sys.argv[1])
    p = factor(n)
    if p is None:
        print(1)
    else:
        print(p)
except:
    print(1)