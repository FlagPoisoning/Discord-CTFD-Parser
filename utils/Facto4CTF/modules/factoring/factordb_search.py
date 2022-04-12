from factordb.factordb import FactorDB
from modules.logger import logger,found_prime

def factordb_search(n,args):
	try:
		f = FactorDB(n)
		f.connect()
		res = f.get_factor_list()
		if(len(res))==1:
			return None
		else:
			if(not args.json):
				if(args.verbose):
					logger("[+] factordb attack found :",'log',1,0)
				if not args.quiet:
					logger('[>] Factors=%s'%str(res),'flag',0,1)
				else:
					print(str(res))
			else:
				print('{"method":"factordb","factor":%s}'%(str(res)))
			return res
	except Exception as ex:
		print(ex)
		return None