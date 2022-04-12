import json
import random

from utils.account import *

def check_json(json_config):
	try:
		json.loads(json_config)
		return True
	except ValueError as ex:
		return False

def create(url,cfg):
	if not check_json(cfg):
		return '**[+] Error : Invalid Json**'
	try:
		session = requests.session()

		if not url.startswith("http://") and not url.startswith("https://"):
			url = "https://" + url	
		target = url.rstrip('/')

		if(not Check_Ctfd(session,url)):
			return '**[+] Please provide a valid ctfd url !**'
		else:
			final = ''
			config = json.loads(cfg)

			for user in config["users"]:
				session.cookies.clear()

				if(user[1] == ""):
					user[1] = "%s@tempmail.com"%(''.join(random.choice("abcdefghijklmnopqrstuvwxyz") for i in range(12)))
				if(user[2] == ""):
					user[2] = ''.join(random.choice("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789+-*:/;.") for i in range(12))

				data = {
					"pseudo":user[0],
					"email":user[1],
					"password":user[2],
					"team":config["team"],
					"team_password":config["teampwd"],
					}

				succeed,in_team = Ctfd_Register(session,data,url)

				if(succeed):
					final += "```\n"
					final += f"- {'Name:':<12}\t{data['pseudo']:>12}\n"
					final += f"- {'Password:':<12}\t{data['password']:>12}\n"
					final += f"- {'Email:':<12}\t{data['email']:>12}\n"
					if(in_team):
						final += f"- {'Team:':<12}\t{data['team']:>12}\n"
						final += f"- {'Team Pass:':<12}\t{data['team_password']:>12}\n"

					final += "```"
				else:
					final += "\n [+] Failed To Login/Create the account %s"%user[0]

			return final	


	except Exception as ex:
		print(ex)
		return '**[+] Error : Invalid Config | Check here https://github.com/Vozec/Ctfd-Account-Creator**'