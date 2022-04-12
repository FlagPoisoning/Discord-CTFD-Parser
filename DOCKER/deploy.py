#!/usr/bin/env python3

import os
from random import randint
import sys
import fileinput
import os.path
import re

if(os.path.isfile('Dockerfile')):

	port = 80

	print("Selected Port : "+str(port))
	
	if(len(sys.argv) != 1):
		if(sys.argv[1] == "install"):
			f = open('Dockerfile', "r")
			docker = f.read()
			f.close()
			
			for line in re.findall(r'ENV HTTP_PORT [0-9]{1,5}',docker):
				docker = docker.replace(line,'ENV HTTP_PORT {}'.format(port))
			
			os.remove('Dockerfile')
			f = open('Dockerfile', "a")
			f.write(docker)
			f.close()
			os.system('docker build -t discordbot .')
			os.system('docker run -d --name CTFDBot -p {}:{} discordbot '.format(port, port))
		else:
			os.system('docker start discordbot')
	else:
			print("Syntax : python3 deploy.py install/run")
