#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# _authors_: Leslato, vozec
# _date_ : 14/03/2022


import discord
from discord.ext import commands
from requests import Session
from requests.compat import urljoin, urlparse, urlsplit
from typing import Generator, List, Union
from jinja2 import Template
import logging
import logging.config
import re, os
import json
from datetime import date
import time
from glob import glob
import argparse
import requests
import names
import random
import urllib
import emoji


##### Modify ################################################################################

TOKEN = ''  # Discord bot token
CategoryName = 'CTF'  # Category Channel Name
PREFIX = '?'  # Bot Prefix

#############################################################################################

bot = commands.Bot(command_prefix=PREFIX, description="CTFd Manager BOT", help_command=None)
challenge_list = {}
all_ctf = []
ctf_name = ""
formatflag = ""
threads = 0
session = Session()
logger = logging.getLogger(__name__)
args = {}
CONFIG = {
    'username': None,
    'password': None,
    'nonce_regex': 'name="nonce"(?:[^<>]+)?value="([0-9a-f]{64})"',
    'base_url': None,
    'no_file': None,
    'no_login': None,
    'template': os.path.join(os.path.dirname(os.path.realpath(__file__)), 'templates/default.md'),
    'verbose': logging.INFO,
    'blacklist': r'[^a-zA-Z0-9_\-\. ]',
    'token':None
    }


#############################################################################################

def parse_args():
    global args
    parser = argparse.ArgumentParser(add_help=True, description='This tools is used to create automatically discord threads by scraping ctfd plateform and collecting name , category , description and points of challenges.')
    parser.add_argument("-s", "--save", dest="save", action="store_true", default=False, help="Save all config in differents json files")
    args = parser.parse_args()
    return args

def saveconfig(ctfname=None,formatf=None):
    url = ''
    global ctf_name,args
    if (ctfname == None):
        ctfname = ctf_name

    for i in range(len(all_ctf)):
        if (ctfname in all_ctf[i][1]):
            ctf_name = all_ctf[i][0]
            

    all_ = {}
    for i in range(len(all_ctf)):
        if (ctfname in all_ctf[i][0]):
            all_ = all_ctf[i][1]
            url = all_ctf[i][2]
            formatf = all_ctf[i][3]

    chall = []
    for element in all_.keys():
        obj = all_[element]
        l = {
            'name': obj[3],
            'points': obj[1],
            'solved': obj[2],
            'flag': obj[4],
            'description': obj[0],
            'thread': obj[5],
            'category': obj[6],
            'id': obj[7],
            'file': obj[8]
        }
        chall.append(l)
    data = {
        'name': ctfname,
        'url': url,
        'date': str(date.today()),
        'formatflag':formatf,
        'challenges': chall
    }
    index = 0;
    if (args.save):
        while (os.path.isfile(f'./ctfd/{ctf_name.lower()}/config_{str(index)}.json')):
            index += 1
    elif (os.path.isfile(f'./ctfd/{ctf_name.lower()}/config_0.json')):
        os.remove(f'./ctfd/{ctf_name.lower()}/config_0.json')

    with open(f'./ctfd/{ctf_name.lower()}/config_{str(index)}.json', 'w', encoding='utf8') as json_file:
        json.dump(data, json_file, allow_nan=True)

    print(f'[+] Ctfd saved in config_{str(index)}.json')

def load(ctx=None):
    global challenge_list, ctf_name, all_ctf, formatflag
    allctf_directory = glob("./ctfd/*/")       

    for ctf in allctf_directory:
        index = 0
        current_list = {}
        while (os.path.isfile(f'{ctf}/config_{str(index)}.json')):
            index += 1
        path = f'{ctf}config_{str(index - 1)}.json'
        if(os.path.isfile(path)):
            f = open(path)
            content = str(f.read())
            f.close()
            data = json.loads(content)
            current = data["name"]
            formatf = data["formatflag"]
       
            if(ctx == None):
                for chall in data["challenges"]:
                    current_list[f'[{chall["category"]}] {chall["name"]}'] = [chall["description"], chall["points"], chall["solved"], chall["name"], chall["flag"],chall["thread"],chall["category"],chall["id"],chall["file"]]
                challenge_list.update(current_list)
                all_ctf.append([current, current_list,data["url"],formatf])
            else:
                challenge_name = ''
                if hasattr(ctx,'message'):
                    challenge_name = str(ctx.message.channel.name).split('|')[0].split(']')[1].strip()
                else:                    
                    challenge_name = str(ctx.name).split('|')[0].split(']')[1].strip()

                if (f'name": "{str(challenge_name)}", "points": "' in content):
                    for chall in data["challenges"]:
                        current_list[f'[{chall["category"]}] {chall["name"]}'] = [chall["description"], chall["points"], chall["solved"], chall["name"], chall["flag"],chall["thread"],chall["category"],chall["id"],chall["file"]]
                    challenge_list.update(current_list)
                    all_ctf.append([current, current_list,data["url"],formatf])

            ctf_name = current
            formatflag = formatf
            print(f"\n [+] Challenges loaded !\n")

#############################################################################################

async def fetch(ctx,url: str) -> Union[List[dict], dict]:
    logger.debug(f'Fetching {url}')
    res = session.get(url)
    if '{\"message' in res.text:
        msg = res.json()['message']
        await ctx.send(f'** [+] {msg}**')
    elif not res.ok or not res.json()['success']:
        logger.error('Failed fetching challenge!')
        #return []
        exit(1)
    else:
        return res.json()['data']

def get_nonce() -> str:
    res = session.get(urljoin(CONFIG['base_url'], '/login'))
    return re.search(CONFIG['nonce_regex'], res.text).group(1)

def setup(username, password, url):
    CONFIG['base_url'] = url
    CONFIG['username'] = username
    CONFIG['password'] = password
    logging.basicConfig(
        level=CONFIG['verbose'],
        format='%(asctime)s %(levelname)s %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    logging.addLevelName(logging.ERROR, '[-]')
    logging.addLevelName(logging.INFO, '[+]')
    logging.addLevelName(logging.DEBUG, '[*]')

async def login(ctx):
    global CONFIG
    resp = requests.get(CONFIG['base_url']).text
    if('https://www.google.com/recaptcha/api.js' in resp  and CONFIG['token'] == None):
        logger.error('Recaptcha Detected !!')        
        await ctx.send('**[+] Recaptcha Detected !!**')
        await ctx.send(f'** ->  use: {PREFIX}token "your token"**')
        return None
    elif('https://www.google.com/recaptcha/api.js' in resp  and CONFIG['token'] != None):
        await ctx.send('**[+] Login using token ...**')
        session.headers.update({"Content-Type": "application/json"})
        session.headers.update({"Authorization": f"Token {CONFIG['token']}"})
        resp = session.get(CONFIG['base_url']+'/api/v1/users/me').text
        if('success\": true' in resp):
            CONFIG['username'] = json.loads(resp)["data"]["name"]
            return True
        else:
            msg = json.loads(resp)["message"]
            await ctx.send(f"```\nMessage:\n{msg}```")
            return False
    else:
        nonce = get_nonce()
        logger.debug(f'Nonce: {nonce}')
        res = session.post(
            urljoin(CONFIG['base_url'], '/login'),
            data={
                'name': CONFIG['username'],
                'password': CONFIG['password'],
                'nonce': nonce,
            }
        )
        if 'incorrect' in res.text:
            logger.error('Impossible to Login With those credentials')
            return False
        elif 'success\": true' in session.get(CONFIG['base_url']+'/api/v1/users/me').text:
            return True
        else:
            return False
    return False

async def get_challenges(ctx):
    logger.debug('Getting challenges ...')
    challenges = await fetch(ctx,urljoin(CONFIG['base_url'], '/api/v1/challenges'))
    result = []
    for challenge in challenges:
        try:
            res = await fetch(ctx,urljoin(CONFIG['base_url'], f'/api/v1/challenges/{challenge["id"]}'))
            file = []
            if('files' in res):
                file = res['files']
            category = res['category']
            name = res['name'].replace(' ','_')        
            description = str(res['description']).replace('\r', '').replace('\n', '')
            points = str(res['value'])
            result.append([category, name, description, points,challenge["id"],file])
        except Exception as ex:
            print("Error during fetching/grabbing a challenge")
            pass        
    return sorted(result)    

async def start_ctfd_part(ctx, username, password, url, ChannelName):
    setup(username, password, url)  # creation des setup pour le login
    print(f"\n[+] Trying to login to : {url}")  # Login to CTFD
    islogged = await login(ctx)
    if islogged != None:
        if islogged:
            await CreateChannel(ctx, ChannelName)
            print(f"\n[>] Logged in with user: {CONFIG['username']}")
            await ctx.send(f"**[+] Logged in with user: {CONFIG['username']}**")
            channel = discord.utils.get(bot.get_all_channels(), name=ChannelName)           # Success
            await start(ctx, channel)  # Start
        else:
            await ctx.reply("**Invalid Credentials or URL**")                               # Invalid Creds

#############################################################################################

def genaccount(ctx):
    ctfname = str(ctx.channel)
    url = ''
    if(len(challenge_list.keys()) == 0):
        load()

    for i in range(len(all_ctf)):
        if (ctfname in all_ctf[i][0]):
            url = all_ctf[i][2]
    if(url == ''):
        return None
    else:
        req = requests.session()
        pseudo = names.get_last_name()+str(random.randint(1,99))
        user = {
            "pseudo":pseudo,
            "email":pseudo+'@tempr.email',
            "password":''.join(random.choice("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789+-*:/;.") for i in range(12)),
            "team":pseudo+"_Team",
            "team_password":''.join(random.choice("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789+-*:/;.") for i in range(12)),
            }

        if(register(req,user,url)):
            return user
        else:
            return None

def verifmail(session):
    mail = pseudo+'@tempr.email'
    post = {
        "LocalPart":mail,
        "DomainType":"public",
        "DomainId":"1",
        "PrivateDomain":"",
        "Password":"",
        "LoginButton":"Retrieve+mailbox",
        "CopyAndPaste":mail
    }
    resp = session.post("https://tempr.email/",data=post)
    if('Confirm your account' in resp.text):
        reg = r'href=\"https://tempr.email/message-(.*?).htm\"><img src='
        found = re.search(resp.text,reg)
        if(len(found) != 0):
            url = found[0]
            resp2 = session.get(url)        
            if('Click the following' in resp2.text):
                reg2 = r'<a href=\"(.*?)\" rel=\"external'
                found2 = re.search(resp.text,reg)
                if(len(found2) != 0):
                    url2 = found2[0]
                    requests.get(url2)
                    return True
    return False


    return ""

def register(req,user,url):
    try:        
        html = req.get(url + "/register").text
        token = re.search(r"csrfNonce': \"(.*?)\",",html).group(1);
        post = {
            "name":user['pseudo'],
            "email":user['email'],
            "password":user['password'],
            "nonce":token,
            "_submit":"Submit",}
        rep = req.post(url+'/register',post).text
        if('Logout' in rep):
            html = req.get(url + "/teams/new").text
            token = re.search(r"csrfNonce': \"(.*?)\",",html).group(1);
            post = {
                "name":user["team"],
                "password":user["team_password"],
                "_submit":"Create",
                "nonce":token,}
            resp = req.post(url+'/teams/new',post).text
            if('Join Team' not in resp):
                print(f"""\n####################--NEW USER--#####################\n##\tName:\t{user['pseudo']}\n##\tPassword:\t{user['password']}\n##\tEmail\t{user['email']}\n##\tTeam:\t{user['team']}\n##\tTeam Pass:\t{user['team_password']}\n##\tLink\thttps://tempr.email/\n#####################################################\n""")
                return True
        else:
            return None
    except Exception as ex:
        print(ex)
        return None

def b_filesize(l):        
    units = ['B','kB','MB','GB','TB','PB']
    for k in range(len(units)):
        if l < (1024**(k+1)):
            break
    return "%4.2f %s" % (round(l/(1024**(k)),2), units[k])

########### Bot Part ########################################################################

@bot.command
async def on_ready():
    print(f'[+] {bot.user.name} has connected to Discord!')
    await bot.change_presence(status=discord.Status.online, activity=discord.Game(PREFIX + 'help'))

async def createthread(ctx,category,name):
    message = await ctx.send(f'[{category}] {name}')
    if message.content in challenge_list.keys():
        try:
            print("\t\tTrying to Create Thread ...")
            thread = await message.create_thread(name=message.content + f' | {str(challenge_list[message.content][1])}')
            challenge_list[message.content][5] = message.id
            channel = bot.get_channel(message.id)
            if (channel != None):
                await channel.send(f"Points: {str(challenge_list[message.content][1])}")
                await channel.send(f"Description: {str(challenge_list[message.content][0])}")
                if(ctf_name == ""):
                    load()
                if(os.path.isdir(f'./ctfd/{ctf_name}/{category}') == False):
                    os.makedirs(f'./ctfd/{ctf_name}/{category}/{name}', exist_ok=True)
                elif(os.path.isdir(f'./ctfd/{ctf_name}/{category}/{name}') == False):
                    os.makedirs(f'./ctfd/{ctf_name}/{category}/{name}', exist_ok=True)
                f = open(f"./ctfd/{ctf_name}/{category}/{name}/README.md", "a")
                f.write(f"Description: {str(challenge_list[message.content][0])}\nPoints: {str(challenge_list[message.content][1])}")
                f.close()
            return thread
        except Exception as ex:
            print('\t' + str(ex))
            print(f'\t[+] Failed to Create Channel: {message.content}')
            if ('We are being rate limited' in str(ex)):
                print('\t\t[+] Timeout ! Waiting 5 seconds')
                time.sleep(5000)
            return None
    else:
       print(f"\t\tThread {message.content} already exist")
       return None

async def start(ctx, channel):
    global threads, challenge_list, all_ctf, ctf_name,formatflag
    hostname = urlparse(CONFIG['base_url']).hostname
    template = Template(open(CONFIG['template']).read())
    print("\n[+] Printing Challenges:")
    challenges = await get_challenges(ctx)
    thread_context = None
    current_list = {}
    if(formatflag == None):
        formatflag = 'flag'
    for challenge in challenges:                                                        # Scraping ...
        threads = 1
        category = challenge[0]
        name = challenge[1]
        description = challenge[2]
        points = challenge[3]
        id_ = challenge[4]
        file = challenge[5]
        current_list[f'[{category}] {name}'] = [description, points, False, name, "",0,category,id_,file]
        if(f'[{category}] {name}' not in challenge_list.keys()):
            challenge_list.update(current_list)
            thread_context = await createthread(channel,category,name)
            if(thread_context != None):
                for chall in file:
                    url = str(CONFIG['base_url'])+str(chall)
                    resp = requests.head(url).headers
                    if(hasattr(resp,"content-length")):
                        size = int(resp["content-length"])
                        if int(size)//(1024*1024) <= 50:
                            file_resp = requests.get(url, allow_redirects=True)
                            file_name = os.path.basename(file_resp.url).split('?')[0]
                            path_file = f'./ctfd/{ctf_name}/{category}/{name}/{file_name}'
                            open(path_file,'wb').write(file_resp.content)
                            res_file = os.popen(f'file "{path_file}"').read().split(f'/{name}/{file_name}')[1]
                            msg = f"**File**: {file_name}\n**Size**: {b_filesize(size)}\n**Info**: {res_file}"
                            if int(size)//(1024*1024) > 7.50:
                                msg += f'\n**Link**: {url}'
                                await thread_context.send(msg)
                            else:
                                await thread_context.send(msg+'```', file=discord.File(path_file))
        else:
            challenge_list.update(current_list)
        print(f'\n  [{category}] {name}')
        print("   [Points] " + str(points))
        print("   [Description] " + str(challenge_list[f'[{category}] {name}'][0]))
    all_ctf.append([ctf_name, current_list,CONFIG['base_url'],formatflag])
    threads = 0

@bot.command()
async def format(ctx,formatf):
    global formatflag
    if len(challenge_list.keys()) == 0:
        load(ctx)
    if(formatf == None):
        await ctx.send('Empty FlagFormat')
    else:
        formatflag = formatf.replace('{','').replace('}','')
        ChannelName = str(ctx.message.channel)
        saveconfig(ctf_name)
        await ctx.send(f' [+] Flag format as been changed: {formatflag}'+r'{}')

@bot.command()
async def gen(ctx):
    print(f"\n[+] Creating account ...\n")
    await ctx.send('**Creating account ...**')
    user = genaccount(ctx)
    if(user != None): 
        print(user)
        await ctx.send(f"""```\n--NEW USER--\nName:\t{user['pseudo']}\nPassword:\t{user['password']}\nEmail\t{user['email']}\nTeam:\t{user['team']}\nTeam Pass:\t{user['team_password']}\nLink\thttps://tempr.email/\n```""")
    else:
        await ctx.send("Failed to Create account ...")

@bot.command()
async def token(ctx,token=None):
    global CONFIG
    if(token == None):
        await ctx.send("**[+] Empty token !!**")
    else:
        CONFIG['token'] = token
        await ctx.message.delete()
        await ctx.send("**[+] Token Stored **")

@bot.command()
async def flagged(ctx, flag=None):
    global ctf_name    
    print("[+] FUNCTION -> Flagged:")
    if ctx.author.guild_permissions.manage_channels or 1==1:
        Thread_name = ctx.message.channel.name
        if('|' in str(ctx.message.channel)):
            if Thread_name[0] == "🚩":
                print(f"\n [*] {Thread_name.split('|')[0].strip()} already flagged")
                await ctx.reply(f"**[*] {Thread_name.split('|')[0].strip()} already flagged**")
                return
            new_Thread_name = "🚩" + Thread_name
            print(f"\n [+] {new_Thread_name} Flagged.\n")
            await ctx.message.channel.edit(name=new_Thread_name)
            await ctx.send(new_Thread_name)
            if len(challenge_list.keys()) == 0:
                load(ctx)
            if len(challenge_list.keys()) != 0:
                clean_name = Thread_name.split('|')[0].strip().replace("🚩", "")
                if clean_name in challenge_list.keys():
                    challenge_list[f'{clean_name}'][2] = True
                    if flag is not None:
                        challenge_list[f'{clean_name}'][4] = flag
                        await ctx.send('Flag successfully stored !')
                        try:
                            await ctx.author.send(f':tada:**Your flag as been Stored and the challenge is now completed !**:tada:\n -Challenge: {clean_name}\n -Flag: {flag}')
                        except:
                            pass
                    else:
                        await ctx.send('Empty flag provided ...')
                    saveconfig()
            else:
                await ctx.send('Error in channel finding ...')

            await ctx.message.delete()
        else:
            await ctx.send('Invalid channel for command "flagged"')
    else:
        print('  [*] {0.author} not allowed.'.format(ctx))
        await ctx.send("**[*] You are not allowed to run this command!**")

@bot.command()
async def help(ctx,message=None):
    global PREFIX
    print("[+] FUNCTION -> Help:")  # Help commmand
    helpmsg = f"""
    **Commands:**```
- {PREFIX}CreateCTFD : Create a channel + threads sorted by name
  |_> Usage: {PREFIX}CreateCTFD  <Username> <Password> <Url> <ChannelName>

- {PREFIX}flagged : Store the flag + renamme the challenge thread
  |_> Usage: {PREFIX}flagged ThisIsMySuperFlag (in challenge thread)

- {PREFIX}end : Moove the ctfd channel in other category
  |_> Usage: {PREFIX}end (in ctfd challenge)

- {PREFIX}gen : Generate new random credentials
  |_> Usage: {PREFIX}gen (in ctfd challenge)

- {PREFIX}format : change format flag
  |_> Usage: {PREFIX}format flag

- {PREFIX}token : set token account to login & bypass recaptcha
  |_> Usage: {PREFIX}token mytoken
```"""
    await ctx.send(helpmsg)


@bot.command()
async def CreateCTFD(ctx, Username=None, Password=None, Url=None, ChannelName=None,formatf=None):    # Create CTFD Channels
    global ctf_name, challenge_list, formatflag
    if(len(challenge_list.keys()) == 0):
        load()
    print("[+] FUNCTION -> CreateCTFD:")
    if Username == None or Password == None or Url == None or ChannelName == None:      # Break if invalid Settings
        print(" [*] Bad arguments")
        await help(ctx)
    ctf_name = ChannelName
    if(formatf != None):
        formatflag = formatf.replace('{','').replace('}','')
    if ctx.author.guild_permissions.manage_channels:  # Parsing CTFD
        print(" [+] Running the important part")
        await start_ctfd_part(ctx, Username, Password, Url, ChannelName)
        print("[+] Thread Creation END")
        saveconfig(ChannelName)

    else:
        print(' [*] {0.author} not allowed.'.format(ctx))
        await ctx.send("**[*] You are not allowed to run this command!**")              # Action Not Permitted

async def CreateChannel(ctx, ChannelName):
    global CategoryName, challenge_list
    print("  [+] FUNCTION -> Create Channel:")
    guild = ctx.guild
    if ctx.author.guild_permissions.manage_channels:
        if (discord.utils.get(bot.get_all_channels(), name=ChannelName) == None):       # If channel does not Exist
            challenge_list = {}
            if not os.path.isdir(f'./ctfd/{ChannelName.lower()}'):
                os.mkdir(f'./ctfd/{ChannelName.lower()}')
            print('  [+] Creating Channel "{0}" By {1.author}.'.format(ChannelName, ctx))
            if(CategoryName not in str(list(bot.get_all_channels()))):
                await ctx.guild.create_category(CategoryName)
            category = discord.utils.get(guild.categories, name=CategoryName)
            await guild.create_text_channel(ChannelName, category=category)
    else:
        print('  [*] {0.author} not allowed.'.format(ctx))
        await ctx.send("**[*] You are not allowed to run this command!**")              # Action Not Permitted

@bot.command()
async def end(ctx):
    if ctx.author.guild_permissions.manage_channels:
        channel_id = ctx.message.channel.id
        channel_object = bot.get_channel(channel_id)
        catego = None
        if(f"End {CategoryName}" not in str(list(bot.get_all_channels()))):
            catego = await ctx.guild.create_category(f"End {CategoryName}")
        else:
            for c in bot.get_all_channels():
                if(f"End {CategoryName}" in str(c)):
                    catego = c
        if(str(channel_object.category) == f"End {CategoryName}"):
            await ctx.send("**[*] Ctf already ended**")
        else:
            await channel_object.edit(category=catego)
            await ctx.send("**[*] Ctf has been moved .**")
            if len(challenge_list.keys()) == 0:
                load()
            await ctx.send(f'**---------- Challenges ----------**')
            for chall in challenge_list.keys():
                if(challenge_list[chall][2] == True):
                    await ctx.send(f'✅ {chall}')
                else:
                    await ctx.send(f'❌ {chall}')
            await ctx.send(f'**------------------------------------**')

        if(args.save):
            alljson =  glob(f"./ctfd/{str(channel_object)}/*.json")
            index = 0;
            while(f'./ctfd/{str(channel_object)}/config_{str(index+1)}.json' in list(alljson)):
                os.remove(f'./ctfd/{str(channel_object)}/config_{str(index)}.json')
                index += 1                            
            if(os.path.isfile(f'./ctfd/{str(channel_object)}/config_{str(index+1)}.json')):
                os.rename(f'./ctfd/{str(channel_object)}/config_{str(index+1)}.json',f'./ctfd/{str(channel_object)}/config_{str(index)}.json')

    else:
        print('  [*] {0.author} not allowed.'.format(ctx))
        await ctx.send("**[*] You are not allowed to run this command!**")


#############################################################################################

if __name__ == '__main__':
    parse_args()
    if not os.path.isdir('ctfd'):
        os.makedirs('ctfd', exist_ok=True)
    bot.run(TOKEN)