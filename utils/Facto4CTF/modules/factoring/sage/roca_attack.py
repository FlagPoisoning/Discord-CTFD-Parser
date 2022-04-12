import sys
from sage.all import inverse_mod, PolynomialRing, floor, Zmod


def solve(M, n, a, m, XX, invmod_Mn, F, x, beta):
    from sage_functions import coppersmith_howgrave_univariate

    base = int(65537)
    known = int(pow(base, a, M) * invmod_Mn)
    pol = x + known
    t = m + 1
    roots = coppersmith_howgrave_univariate(pol, n, beta, m, t, XX)
    for k in roots:
        p = int(k * M + pow(base, a, M))
        if n % p == 0:
            return p, n // p


def roca(n):
    keySize = n.bit_length()
    if keySize <= 960:
        M_prime = 0x1B3E6C9433A7735FA5FC479FFE4027E13BEA
        m = 5
    elif 992 <= keySize <= 1952:
        M_prime = (0x24683144F41188C2B1D6A217F81F12888E4E6513C43F3F60E72AF8BD9728807483425D1E)
        m = 4
        print("Have you several days/months to spend on this ?")
    elif 1984 <= keySize <= 3936:
        M_prime = 0x16928DC3E47B44DAF289A60E80E1FC6BD7648D7EF60D1890F3E0A9455EFE0ABDB7A748131413CEBD2E36A76A355C1B664BE462E115AC330F9C13344F8F3D1034A02C23396E6
        m = 7
        print("You'll change computer before this scripts ends...")
    elif 3968 <= keySize <= 4096:
        print("Just no.")
        return None
    else:
        print("Invalid key size: {}".format(keySize))
        return None
    beta = 0.1
    a3 = Zmod(M_prime)(n).log(65537)
    order = Zmod(M_prime)(65537).multiplicative_order()
    inf = a3 >> 1
    sup = (a3 + order) >> 1
    XX = floor(2 * n ** 0.5 / M_prime)
    invmod_Mn = inverse_mod(M_prime, n)
    F = PolynomialRing(Zmod(n), implementation="NTL", names=("x",))
    (x,) = F._first_ngens(1)
    chunk_size = 10000
    for inf_a in range(inf, sup, chunk_size):
        inputs = [
            ((M_prime, n, a, m, XX, invmod_Mn, F, x, beta), {})
            for a in range(inf_a, inf_a + chunk_size)
        ]
        from sage.parallel.multiprocessing_sage import parallel_iter
        from multiprocessing import cpu_count
        for k, val in parallel_iter(cpu_count(), solve, inputs):
            if val:
                p = val[0]
                q = val[1]
                print("{}:{}".format(p, q))
                return val
    return "Fail"


if __name__ == "__main__":
    n = int(sys.argv[1])
    try:
        roca(n)
    except Exception as ex:
        print("FAIL")
