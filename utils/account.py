import re
import requests
import random
import json
import os
import names

from utils.logger import logger

def Check_Ctfd(session,url):
    try:
        if('Powered by CTFd' in session.get(url).text):
            return True
        return False
    except Exception as ex:
        logger(' [+] Error during ctfd check : %s'%str(ex),"error",1,0)
        return False


def CheckTeam_Exist(url,req,user):
    try:
        resp = req.get(url+'/teams?field=name&q=%s'%user['team']).text
        all_ = list(zip(*list(re.findall(r'<a href="/teams/(.*?)">(.*?)</a>',resp))))
        if(len(all_) != 0):
            if(user["team"].lower() in list((map(lambda x: x.lower(), all_[1])))):
                return True  
        return False
    except Exception as ex:
        logger(" [+] Error to check if team exist : %s"%str(ex),"error",1,0)
        return False


def CheckUser_Exist(url,req,user):
    try:
        resp = req.get(url+'/users?field=name&q=%s'%user['pseudo']).text.replace("\n","").replace("\t","")
        all_ = list(zip(*list(re.findall(r'<a href="/users/(.*?)">(.*?)</a>',resp))))
        if(len(all_) != 0):
            if(user["pseudo"].lower() in list((map(lambda x: x.lower(), all_[1])))):
                return True  
        return False
    except Exception as ex:
        logger(" [+] Error to check if user exist : %s"%str(ex),"error",1,0)
        return False


def CheckTeam_User(url,req,user):
    try:
        verif = req.get(url+'/api/v1/users/me').text
        if(type(json.loads(verif)["data"]["team_id"]) == int):
            return True
        return False
    except Exception as ex:
        logger(" [+] Error to check user account : %s"%str(ex),"error",1,0)
        return False


def Join_Team(url,req,user):
    try:
        html = req.get(url + "/teams/join").text
        token = re.search(r"csrfNonce': \"(.*?)\",",html).group(1); # Get token csrf
        post = {"name":user["team"],"password":user["team_password"],"_submit":"Join","nonce":token}    # Post Data
        resp = req.post(url+'/teams/join',post).text    # Create Team
        return CheckTeam_User(url,req,user)
    except Exception as ex:  
        logger(" [+] Error to join the team : %s"%str(ex),"error",1,0)
        return False


def Create_Team(url,req,user):
    try:
        html = req.get(url + "/teams/new").text
        token = re.search(r"csrfNonce': \"(.*?)\",",html).group(1); # Get token csrf
        post = {"name":user["team"],"password":user["team_password"],"_submit":"Create","nonce":token}  # Post Data
        resp = req.post(url+'/teams/new',post).text # Create Team
        return CheckTeam_User(url,req,user)
    except Exception as ex:
        logger(" [+] Error during team creation : %s"%str(ex),"error",1,0)
        return False
  

def Register_Account(req,user,url):
    try:
        html = req.get(url + "/register").text     # Get html page        
        token = re.search(r"csrfNonce': \"(.*?)\",",html).group(1);# Get token
        rep = req.post(url+'/register',{"name":user['pseudo'],"email":user['email'],"password":user['password'],"nonce":token,"_submit":"Submit"}).text# Post request
        if('Logout' in rep):
            return True
        return False
    except Exception as ex:
        logger(" [+] Error during registration : %s"%str(ex),"error",1,0)
        return False

def Login_Account(req,user,url):
    try:
        
        if(CheckUser_Exist(url,req,user)):
            # Login to account      
            
            html = req.get(url + "/login").text   # Get html page  
            token = re.search(r"csrfNonce': \"(.*?)\",",html).group(1);# Get token
            rep = req.post(url+'/login',{"name":user['pseudo'],"password":user['password'],"_submit":"Submit","nonce":token}).text# Post request
            if('Logout' in rep):
                return True
            return False
        else:
            # Creating account
            return Register_Account(req,user,url)
        
    except Exception as ex:
        logger(" [+] Error during login : %s"%str(ex),"error",1,0)
        return False

def Ctfd_Register(req,user,url):
    try:
        # Login/Create Account
        if(Login_Account(req,user,url)):
           
           # Check if team exist
            in_team = False
            if not CheckTeam_User(url,req,user):
                if(CheckTeam_Exist(url,req,user)):
                    # Join Team
                    in_team = Join_Team(url,req,user)
                else:
                    # Create Team
                    in_team = Create_Team(url,req,user)

            else:
                logger(" [+] User %s is already in a team "%user["pseudo"],"info",1,0)


            return True,in_team
        else:
            return False,False
    except Exception as ex:
        logger(" [+] Error during registration : %s"%str(ex),"error",1,0)
        return False,False

def RandomAccount(url=''):

    # Check if Url is empty
    if url == '':
        return None
    else:

        ## SANITIZE URL
        if not url.startswith("http://") and not url.startswith("https://"):
            url = "https://" + url  
        url = url.rstrip('/')

        # Create Sessions
        req = requests.session()

        # Gen Random Pseudo
        pseudo = names.get_last_name()+str(random.randint(1,99))

        # Post Data
        user = {
            "pseudo":pseudo,
            "email":pseudo+'@tempr.email',
            "password":''.join(random.choice("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789+-*:/;.") for i in range(12)),
            "team":pseudo+"_Team",
            "team_password":''.join(random.choice("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789+-*:/;.") for i in range(12)),
            }

        # Register 
        res ,in_team= Ctfd_Register(req,user,url)
        if(res):
            return user
        else:
            return None
            
# OLD
# https://pastebin.com/raw/BYMxenM2