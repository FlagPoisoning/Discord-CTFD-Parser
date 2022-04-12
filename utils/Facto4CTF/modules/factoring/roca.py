import time
import os
import threading
import ctypes

from modules.logger import logger,found_prime
from modules.utils import kill_sage

def roca(stop,n,timeout,args):
	try:
		rootpath = '/'.join(os.path.realpath(__file__).split('/')[:-1])

		t = KThread(stop,n,timeout,args,rootpath)
		t.start()

		while(True):
			if(stop.is_cancelled):
				kill_sage()
			
			if not t.is_alive():
				if(t.found):
					stop.cancel()
				break

		return None

	except Exception as ex:
		logger('[+] Error: %s'%str(ex),'error',0,0)

class KThread(threading.Thread):
	def __init__(self, stop,n,timeout,args,rootpath,**keywords):
		super(KThread, self).__init__()
		self.found 		= False
		self.stop  		= stop
		self.n 			= n
		self.timeout  	= timeout
		self.args 		= args
		self.rootpath 	= rootpath
	
	def run(this):
		try:
			p = q = None
			sageresult = os.popen("sage %s/sage/roca_attack.py %s"%(this.rootpath,str(this.n))).read()
			if "FAIL" not in sageresult and ":" in sageresult:
				sageresult = sageresult.strip()
				p, q = map(int, sageresult.split(":"))  
				if(p*q != this.n or p==1 ):
					return None

				if(not this.args.json):
					if(this.args.verbose):
						logger("[+] roca attack found",'log',1,0)
					if not this.args.quiet:
						logger('[>] P=%s'%str(p),'flag',0,1)
						logger('[>] Q=%s'%str(q),'flag',0,1)
					else:
						print(str(p))
						print(str(q))
				else:
					print('{"method":"roca","factor":[%s,%s]}'%(str(p),str(q)))
				
				this.found = True
				return p,q

			else:
				return None
		except Exception as ex:
			#print(ex)
			return None

