from datetime import datetime

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