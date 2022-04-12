#!/usr/bin/env python3

import argparse
import threading
import time
from modules.logger import logger

# All modules
from modules.factoring.factordb_search import factordb_search
from modules.factoring.fermat import fermat
from modules.factoring.pollard_rho import pollard_rho
from modules.factoring.pollard_p_1 import pollard_p_1
from modules.factoring.z3 import z3
from modules.factoring.smallq import smallq
from modules.factoring.mersene_prime import mersene_prime
from modules.factoring.mersenne_pm1_gcd import mersenne_pm1_gcd
from modules.factoring.euler import euler
from modules.factoring.fibonacci_gcd import fibonacci_gcd
from modules.factoring.noveltyprimes import noveltyprimes
from modules.factoring.fermat_numbers_gcd import fermat_numbers_gcd
from modules.factoring.brent import brent
from modules.factoring.ecm import ecm
from modules.factoring.ecm2 import ecm2
from modules.factoring.smallfraction import smallfraction
from modules.factoring.roca import roca
from modules.factoring.qicheng import qicheng

#from modules.factoring.primorial_pm1_gcd import primorial_pm1_gcd

## All functions
all_ = {
        'fermat':fermat,
        'ecm':ecm,
        'ecm2':ecm2,
        'pollard_rho':pollard_rho,
        'pollard_p_1':pollard_p_1,
        'z3':z3,
        'smallq':smallq,
        'mersene_prime':mersene_prime,
        'mersenne_pm1_gcd':mersenne_pm1_gcd,
        'euler':euler,
        'fibonacci_gcd':fibonacci_gcd,
        # 'fermat_numbers_gcd':fermat_numbers_gcd,
        'brent':brent,
        'smallfraction':smallfraction,
        'roca':roca,
        'qicheng':qicheng
        # 'primorial_pm1_gcd':primorial_pm1_gcd
}

class thread_stop:
   def __init__(self):
       self.is_cancelled = False

   def cancel(self):
       self.is_cancelled = True

def waiter(timeout,stop):
    for k in range(timeout):
        time.sleep(k)
        if(stop.is_cancelled):
            return
    stop.cancel()
    return
    
def header():
    ## header
    logger(r"""
    ______           __        __ __  ________  ____
   / ____/___ ______/ /_____  / // / / ____/ /_/ __/
  / /_  / __ `/ ___/ __/ __ \/ // /_/ /   / __/ /_
 / __/ / /_/ / /__/ /_/ /_/ /__  __/ /___/ /_/ __/
/_/    \__,_/\___/\__/\____/  /_/  \____/\__/_/
                                                                                                                      
""",'warning',0,0)


def parse_args():
    ## Parse All arguments
    parser = argparse.ArgumentParser(add_help=True, description='This tool is used to try out different factoring techniques. Mainly used in CTF.')
    parser.add_argument("-n",dest="number",type=int,required=True, help="Number to factor")
    parser.add_argument("-a",dest="all_method",action="store_true",default=False, help="Try all algorithm")
    parser.add_argument("-m",dest="algorithm",type=str,help="Choose an algorithm : %s"%str(list(all_.keys())))
    parser.add_argument("-t",dest="timeout",type=int,help="Set Timeout (minutes) (default=5min)")
    parser.add_argument("-v",dest="verbose", action="store_true", default=False, help="Use verbose mode.")
    parser.add_argument("-q",dest="quiet", action="store_true", default=False, help="Use quiet mode.")
    parser.add_argument("-j",dest="json", action="store_true", default=False, help="Use json mode.")
    args = parser.parse_args()
    return args


def GetAlg(all_method,algorithm):
    ## Recap algo. to use
    if(all_method):
        return list(all_.items())
    else:
        return [name for name in all_.items() if(algorithm == name[0])]

def main():
    args = parse_args()

    ## Check input
    if(not args.quiet): header()
    if(not args.all_method and args.algorithm == None):logger('[+] Choose an algorithm (-m ) or test all (-a)','error',0,0)

    ## Get algorithm
    All_Alg = GetAlg(args.all_method,args.algorithm)

    ## Check on factorDB first
    if(factordb_search(args.number,args) == None):
        ## Init Thread list
        all_thread = []
        stopper = thread_stop()
        timeout = 5*60

        if(args.timeout != None):
            timeout = args.timeout*60

        for k in range(len(All_Alg)):

            ## Log
            if(not args.quiet and args.verbose):logger('[+] Starting %s attack '%All_Alg[k][0],'info',0,0)   

            ## Create Thread
            t1 = threading.Thread(target = All_Alg[k][1], args = (stopper,args.number,timeout,args))
            all_thread.append(t1)
        

        ## Start Thread
        [t.start() for t in all_thread]

        t_timeout = threading.Thread(target = waiter, args = (timeout,stopper))
        t_timeout.start()

        ## Wait For all Thread
        [t.join() for t in all_thread]

        stopper.cancel()


if __name__ == '__main__': 
    main()