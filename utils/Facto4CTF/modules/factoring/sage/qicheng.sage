import sys
sys.setrecursionlimit(10000)

from sage.parallel.multiprocessing_sage import parallel_iter
from multiprocessing import cpu_count

def factor(n,attempts=50):
    Consts = {}
    Consts['0'] = 0
    Consts['1'] = 1
    Consts['2'] = 2
    Consts['3'] = 3
    Consts['1728'] = 1728
    js = [0, (-2^5)^3, (-2^5*3)^3 ,(-2^5*3*5*11)^3, (-2^6*3*5*23*29)^3]


    def corefunc(n,js,Consts):
        R = Integers(int(n))
        
        for j in js:
            if j == Consts['0']:
                a = R.random_element()
                E = EllipticCurve([Consts['0'], a])

            else:
                a = R(j)/(R(Consts['1728'])-R(j))
                c = R.random_element()
                E = EllipticCurve([Consts['3']*a*c^Consts['2'], Consts['2']*a*c^Consts['3']])

            x = R.random_element()
            z = E.division_polynomial(n, x)
            g = gcd(z, n)
            if g > Consts['1']:return g

    cpus = cpu_count()
    if attempts > cpus:
        A = cpus
    else:
        A = attempts
    B = int(attempts/cpus)
    for i in range(0,B+1):
        inputs = [((n,js,Consts,),{})] * A
        for k, val in parallel_iter(A, corefunc,inputs):
            if val != None:
                return val

if __name__ == "__main__":
    print(factor(Integer(sys.argv[1])))
