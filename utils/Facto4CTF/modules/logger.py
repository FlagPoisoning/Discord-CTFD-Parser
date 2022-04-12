from datetime import datetime
import subprocess

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

all_context = {
    'info':bcolors.WARNING,
    'flag':bcolors.OKGREEN,
    'log':bcolors.OKBLUE,
    'error':bcolors.FAIL,
    'warning':bcolors.OKCYAN,
    None:''
}

def logger(message,context=None,newline=0,tab=0):
    final = ""
    final += '\n'*newline
    now = datetime.now()
    final += now.strftime("%H:%M:%S")
    final += " | "
    final += all_context[context]
    final += '\t'*tab
    final += ' '
    final += message
    final += bcolors.ENDC
    print(final)

def found_prime(p,q,stop,args,method):
    if(not stop.is_cancelled):
        stop.cancel()
        if(not args.json):
            if(args.verbose):
                logger("[+] %s attack found :"%method,'log',1,0)
                
            if not args.quiet:
                logger('[>] P=%s'%str(p),'flag',0,1)
                logger('[>] Q=%s'%str(q),'flag',0,1)
            else:
                print(str(p))
                print(str(q))
        else:
            print('{"method":"%s","factor":[%s,%s]}'%(method,str(p),str(q)))

