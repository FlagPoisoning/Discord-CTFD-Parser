#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# _authors_: Leslato, vozec
# _date_ : 14/03/2022


import discord
from discord.ext import commands
from requests import Session
from requests.compat import urljoin, urlparse, urlsplit
import re, os
import json
from datetime import date
import time
from glob import glob
import argparse
import requests
import random
import urllib
import emoji
import subprocess

from utils.logger import logger
import utils.analyse_file
import utils.account
import utils.help
import utils.cypher
import utils.parser
import utils.ctftime
import utils.crypto
import utils.createteam

from utils.other import sizeok,b_filesize,download,rdnname,findfile,finddirectory

##### Modify ################################################################################

TOKEN           = ''  # Discord bot token
CategoryName    = 'CTF'  # Category Channel Name
PREFIX          = '?'  # Bot Prefix

#############################################################################################

bot = commands.Bot(command_prefix=PREFIX, description="CTFd Manager BOT", help_command=None)
challenge_list = {}
all_ctf = []
ctf_name = ""
formatflag = ""
session = Session()
args = {}

CONFIG = {
    'PREFIX':PREFIX,
    'username': None,
    'password': None,
    'base_url': None,
    'token':None
    }

#############################################################################################

def parse_args():
    global args
    parser = argparse.ArgumentParser(add_help=True, description='This tools is used to create automatically discord threads by scraping ctfd plateform and collecting name , category , description and points of challenges.')
    parser.add_argument("-a", "--analyse", dest="analyse_file", action="store_true", default=False, help="Analyse all challenges downloaded files")
    args = parser.parse_args()
    return args

def saveconfig(ctfname=None,formatf=None):

    url = ''
    global ctf_name,args

    ## Getting actual CTF 
    if (ctfname == None):
        ctfname = ctf_name

    all_ = {}
    ## Check if name is in list
    for i in range(len(all_ctf)):
        if (ctfname in all_ctf[i][1].keys()): 
            ctf_name = all_ctf[i][0]

        if (ctfname in all_ctf[i][0]):
            all_ = all_ctf[i][1]
            url = all_ctf[i][2]
            formatf = all_ctf[i][3]

    # Starting to create the save object with all info

    # Getting all challenge 
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

    # Final Object
    data = {
        'name': ctfname,
        'url': url,
        'date': str(date.today()),
        'formatflag':formatf,
        'challenges': chall
    }

    current_dir = os.path.dirname(os.path.abspath(__file__))

    # If save option > New file
    path = '%s/ctfd/%s/config_0.json'%(current_dir,ctf_name.lower())

    # remove old config
    if os.path.isfile(path):
        os.remove(path)

    # Save the file in Json Format
    with open(path, 'w', encoding='utf8') as json_file:
        json.dump(data, json_file, allow_nan=True)

    logger('[+] Ctfd saved in config_0.json','info',1,1)

def load(ctx=None,display_message=None):
    global challenge_list, ctf_name, all_ctf, formatflag

    # Last creation date   
    lasttime    = 0
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Enum in all ctfd
    for ctf in  glob("%s/ctfd/*/"%current_dir):

        current_list = {}
        path = '%sconfig_0.json'%ctf

        # If file exist
        if(os.path.isfile(path)):

            # Update last file date by default
            t = os.path.getmtime(path)
            if(t > lasttime or lasttime == 0):
                ctf_name = ctf.split('/ctfd/')[1].replace('/','')
                lasttime = t

            # Read config.json
            f = open(path)
            content = str(f.read())
            f.close()
            data = json.loads(content)

            #General infos
            current = data["name"]
            formatf = data["formatflag"]

            # If no challenge selected > Load all
            cpt = 0;

            # Add in challenge list
            for chall in data["challenges"]:
                cpt += 1
                current_list['[%s] %s'%(chall["category"],chall["name"])] = [chall["description"], chall["points"], chall["solved"], chall["name"], chall["flag"],chall["thread"],chall["category"],chall["id"],chall["file"]]
            challenge_list.update(current_list)
            all_ctf.append([current, current_list,data["url"],formatf])

            ##OLD : https://pastebin.com/raw/NA03DapP > Load only challenge if found > Changed bcs useless
           
            # Load format Flag  
            formatflag = formatf

            logger("%s challenges loaded from : %s"%(str(cpt),current),"log",0,1)

    if(display_message != True):
        logger(f"All Challenges loaded !","info",1,1)

def setup(username, password, url):
    CONFIG['base_url'] = url
    CONFIG['username'] = username
    CONFIG['password'] = password

async def createthread(ctx,category,name):
    # OLD : 04/04/2022 https://pastebin.com/raw/6MpwZB5t
    message = await ctx.send('[%s] %s'%(category,name))

    # If is real challenge
    if message.content in challenge_list.keys():
        try:
            # Create Thread
            logger("Trying to Create Thread ...","info",1,2)
            challenge = challenge_list[message.content]

            thread = await message.create_thread(name=message.content + ' | %s'%str(challenge[1]))
            challenge[5] = message.id
            channel = bot.get_channel(message.id)

            # If channel created succesfully
            if (channel != None):
                await channel.send("Points: %s"%str(challenge[1]))
                await channel.send("Description: %s"%str(challenge[0]))

                # If not challenge > Load
                if (ctf_name == "") : load()

                # Create directory
                current_dir = os.path.dirname(os.path.abspath(__file__))

                if(not os.path.isdir('%s/ctfd/%s/%s/%s'%(current_dir,ctf_name,category,name))):
                    os.makedirs('%s/ctfd/%s/%s/%s'%(current_dir,ctf_name,category,name), exist_ok=True)

                # Save info
                f = open("%s/ctfd/%s/%s/%s/README.md"%(current_dir,ctf_name,category,name), "a")
                f.write("Description: %s\nPoints: %s"%(str(challenge[0]),str(challenge[1])))
                f.close()

            return thread
        except Exception as ex:

            # Exception > Ban ip Rate limited
            logger('Failed to Create Channel: %s'%message.content,"error",1,0)
            logger(str(ex),"error",0,0)
            if ('We are being rate limited' in str(ex)):
                logger('Timeout ! Waiting 5 seconds',"error",0,2)
                time.sleep(5000)

            return None
    else:
       logger("Thread %s already exist"%message.content,"error",1,1)
       return None

async def start(ctx, channel):
    global challenge_list, all_ctf, ctf_name,formatflag

    # Parse infos
    hostname = urlparse(CONFIG['base_url']).hostname
    
    logger("Printing Challenges:","info",1,1)
    
    # Parsing challenges
    challenges = await utils.parser.get_challenges(ctx,CONFIG,session)

    thread_context = None
    current_list = {}
    if(formatflag == None or formatflag == ''):
        formatflag = 'flag'

        # Enum on All channels
    for challenge in challenges:# Scraping ...
        
        # Info on the challenge
        category        = challenge[0]
        name            = challenge[1]
        description     = challenge[2]
        points          = challenge[3]
        id_             = challenge[4]
        file            = challenge[5]
        current_list[f'[{category}] {name}'] = [description, points, False, name, "",0,category,id_,file]
        
        # IF not already printed 
        
        if(f'[{category}] {name}' not in challenge_list.keys()):
            challenge_list.update(current_list)
            thread_context = await createthread(channel,category,name)
            if(thread_context != None):

                # Send all file + analyse file if needed
                for chall in file:
                    try:

                        # Check if size is not big
                        url = str(CONFIG['base_url'])+str(chall)
                        size = int(requests.head(url).headers["content-length"])
                        if int(size)//(1024*1024) <= 50:

                            # Curl file
                            file_resp = requests.get(url, allow_redirects=True)
                            file_name = os.path.basename(file_resp.url).split('?')[0]
                            current_dir = os.path.dirname(os.path.abspath(__file__))
                            path_file = '%s/ctfd/%s/%s/%s/%s'%(current_dir,ctf_name,category,name,file_name)

                            # Save file
                            open(path_file,'wb').write(file_resp.content)
                            res_file = os.popen('file "%s"'%path_file).read().split('/%s/%s'%(name,file_name))[1]
                            msg = "**File**: %s\n**Size**: %s\n**Info**: %s"%(file_name,b_filesize(size),res_file)

                            # If size not OK
                            if int(size)//(1024*1024) > 7.50:
                                msg += '\n**Link**: %s'%url
                                await thread_context.send(msg)
                            else:
                                # Send file
                                await thread_context.send(msg+'```', file=discord.File(path_file))

                            # If -a option > Analyse
                            if(args.analyse_file):  
                                await analyse_file(thread_context,path_file,formatflag,'[%s] %s'%(category,name))

                    except Exception as ex:
                        logger('Error in challenge: %s | %s'%(name,str(ex)),"error",0,1)
        else:
            challenge_list.update(current_list)


        # Save 
        # If already exist
        saved = False
        for ctf in all_ctf:
            if(ctf_name == ctf[0]):
                saved = True
                for chall in current_list.keys():
                    if(chall not in ctf[1].keys()):
                        ctf[1][str(current_list[chall])] = current_list[chall]

        # If not created
        if(saved == False):
            all_ctf.append([ctf_name, current_list,CONFIG['base_url'],formatflag])

        # Save all 
        saveconfig(ctf_name)

        # Display info
        logger(f'[{category}] {name}',"log",0,2)
        logger("[Points] " + str(points),"log",0,2)
        logger("[Description] " + str(challenge_list[f'[{category}] {name}'][0]),"log",0,2)

async def confirmDL(ctx,filename):
    
    # Embed Message 
    embed = discord.Embed(title="Download Confirmation", description="File: "+filename,color=0x00ff00)
    message = await ctx.send(embed=embed)
    for emote in ["✅","❌"]:
        await message.add_reaction(emote)

    for i in range(10):
        time.sleep(1)
        message = await message.edit(content=message.content)
        react = ''  
        for elem in message.reactions:
            react += emoji.demojize(str(elem))+'|'+str(elem.count)
        if(emoji.demojize(":check_mark_button:|2") in react):
            return True
        elif(emoji.demojize(":cross_mark:|2") in react):
            return False
    return False

async def createchannel(ctx, ChannelName):
    global CategoryName, challenge_list
    logger("FUNCTION -> Create Channel:")
    guild = ctx.guild

    #Grab + Check if Permissions are fine
    if ctx.author.guild_permissions.manage_channels:

        # Check If channel does not Exist
        if (discord.utils.get(bot.get_all_channels(), name=ChannelName) == None):
            challenge_list = {}
            if not os.path.isdir(f'./ctfd/{ChannelName.lower()}'):
                os.mkdir('./ctfd/%s'%ChannelName.lower())
            logger('Creating Channel "{0}" By {1.author}.'.format(ChannelName, ctx),"info",1,1)

            # Check If Category does not Exist
            if(CategoryName not in str(list(bot.get_all_channels()))):
                await ctx.guild.create_category(CategoryName)
    
            category = discord.utils.get(guild.categories, name=CategoryName)
            await guild.create_text_channel(ChannelName, category=category)
    else:
        # Action Not Permitted
        logger('{0.author} not allowed.'.format(ctx),"error",1,2)
        await ctx.send("**[*] You are not allowed to run this command!**")  

async def list_FileQueue(ctx,filename=None,formatflag=None,clean_name=None):
    
    # List Files to analyses
    files = []
    
    if(filename == None):
        return files

     # IF is url
    if '?' in filename:
        filename = filename.split('?')[0]

    if clean_name in challenge_list.keys():
        # Global Infos

        category = challenge_list[clean_name][6]
        name = challenge_list[clean_name][3]
        current_dir = os.path.dirname(os.path.abspath(__file__))

        #current_path = '%s/ctfd/%s/%s/%s/'%(current_dir,ctf_name,category,name)
        #current_base = '%s/ctfd/'%(current_dir)

        # Old : https://pastebin.com/raw/gWc0Skux
        found_f = findfile(filename)
        for current_path in found_f:

            # Ask for check this file :
            # if confirmanalyse(path):
            files.append(current_path.replace("./ctfd",current_dir+'/ctfd'))

        if('://' in filename and await confirmDL(ctx,filename)):
            found_d = finddirectory(name)
            for current_directory in found_d:
                # if confirmanalyse(path):
                # Download  
                name_splitted = filename.split('/')[-1]
                downloaded_file_path = current_directory.replace("./ctfd",current_dir+'/ctfd')+'/'+name_splitted
                if(download(filename,downloaded_file_path) == True):
                    files.append(downloaded_file_path)

    elif(filename != None):  
        
        if('://' in filename and await confirmDL(ctx,filename)):
            # Download
            rdn = rdnname()
            namefile = filename.split('/')[-1]
            downloaded_file_path = "/tmp/"+rdn+"_"+namefile
            if(download(filename,downloaded_file_path) == True):
                files.append(downloaded_file_path)

    return files

async def analyse_file(ctx,filename=None,formatflag=None,clean_name=None):

    challenge = None

    if (len(ctx.message.attachments) > 0):filename = ctx.message.attachments[0].url

    # Get Challenge Name
    if hasattr(ctx,'message'):
        challenge = ctx.message.channel
    else:
        challenge = ctx

    # Reload Challenge if no loaded
    if len(challenge_list.keys()) == 0: load(ctx)

    # Cleaned name without 🚩 
    if(clean_name == None): clean_name = challenge.name.split('|')[0].strip().replace("🚩", "")

    # Sanitize Format flag
    if(formatflag == None or formatflag == ''):formatflag = 'flag'
    formatflag = formatflag.replace('{','').replace('}','')
    

    # List all path of file
    all_files = await list_FileQueue(ctx,filename,formatflag,clean_name)


    if(analyse_file == []):
        await ctx.send('**[+] Challenge not found ...**')
    else:

        # Analyses Files
        found = []

        for f in all_files:
            if(os.path.isfile(f)):

                logger('Analysing %s'%f,"info",1,1)
                await ctx.send(f'** [+] Analysing**')
                
                # Call analyse function
                resp,embed_text,flag_found = utils.analyse_file.analysis(f,formatflag)
                
                # Add flag found to the list 
                found += flag_found

                # Embed
                embed = discord.Embed(title="Analysis Result", description="File: "+os.path.basename(f),color=0x00ff00)
                embed.add_field(name="Info : \n", value=embed_text)
                await ctx.send(embed=embed)

                # Send Result
                for element in resp:
                    if type(element) == list :

                        path_report = element[1]

                        if(os.path.isfile(path_report)):
                            
                            # Upload file is Lengt < 8mb
                            cnt = element[0]
                            try:

                                if sizeok(path_report):
                                    await ctx.send(cnt,file=discord.File(path_report))
                                    # Remove File
                                    os.system('rm %s'%path_report)
                                else:
                                    await ctx.send('%s : File is too big %s'%(cnt,path_report))

                            except Exception as ex:
                                logger(str(ex),"error",1,1)
                                pass                            
                    else:              
                        await ctx.send(element)

                logger('End Analysing',"info",1,0)

                # Send Flag Founded
                if found != []:
                    await ctx.send('**[+] Found: **\n```%s```'%found)

                # End
                await ctx.send('**[+] End Analysing**')

########### Bot Part ########################################################################

@bot.event
async def on_ready():
    # Handler bot on startup
    logger('%s has connected to Discord!\n'%bot.user.name,"info",1,2)
    await bot.change_presence(status=discord.Status.online, activity=discord.Game(PREFIX + 'help'))

@bot.command()
async def change(ctx):
    global ctf_name

    # Load challenge from config if empty
    if(all_ctf == []): load()


    # Mapping for discord reaction
    ctf = {}
    mapping = {
        "0":"0️⃣",
        "1":"1️⃣",
        "2":"2️⃣",
        "3":"3️⃣",
        "4":"4️⃣",
        "5":"5️⃣",
        "6":"6️⃣",
        "7":"7️⃣",
        "8":"8️⃣",
        "9":"9️⃣"
    }

    # Convert index to discord Emoji
    for i in range(len(all_ctf[:10])):
        ctf[all_ctf[i][0]] = "".join([mapping[letter] for letter in (str(i))])

    # If nb of ctf > 0
    if(len(ctf) != 0):

        # Create WebHook + send
        embed = discord.Embed(title="Select CTF", description="Name:"+"".join([(f"\n  [+] {name.upper():>15} : {ctf[name]:>15}") for name in ctf.keys()]),color=0x00ff00)
        message = await ctx.send(embed=embed)
        
        # Add reaction On message
        for emote in ctf.values():
            await message.add_reaction(emote)

        # Wait 10 Seconds 
        for i in range(10):
            time.sleep(1)

            # Get Current Reaction on the message
            message = await message.edit(content=message.content)
            react = {}   
            for elem in message.reactions:
                react[emoji.demojize(str(elem))]= elem.count

            mapping2 = {
                ":keycap_0:":0,
                ":keycap_1:":1,
                ":keycap_2:":2,
                ":keycap_3:":3,
                ":keycap_4:":4,
                ":keycap_5:":5,
                ":keycap_6:":6,
                ":keycap_7:":7,
                ":keycap_8:":8,
                ":keycap_9:":9
            }


            # If Nb of reaction > 1
            for el in list(mapping2.keys())[:len(react.keys())]:
                if(el in mapping2.keys()):
                    if(react[el] > 1):
                        ctf_name = list(ctf.keys())[mapping2[el]]
                        logger("New Ctf Selected : %s"%ctf_name,"info",1,0)
                        await ctx.send("**[+] New Ctf Selected : %s**"%ctf_name)
                        return None
    return None

@bot.command()
async def analyse(ctx,filename=None,formatf=None):
    global formatflag

    # If format flag provided > Replace the other 
    if(formatf != None):
        formatflag = formatf

    await analyse_file(ctx,filename,formatflag)

@bot.command()
async def genteam(ctx,url=None,config=None):

    ##Invalid Parameters
    if(url == None or config == None):
        await ctx.send('**[+] Please provide a valid url and an existing/valid config**')
    else:
        logger('Creating Team on %s'%url,'log',1,0)

        ## Init
        current_dir = os.path.dirname(os.path.abspath(__file__))
        path = current_dir+'/config/%s.json'%(config.replace(".json",""))
        cfg = ''

        ##If invalid config + config does not exist
        if(config != '```' and not os.path.isfile(path)):
            await ctx.send('**[+] Please provide an existing/valid config**')
            msg = '''\n{\n    "team":"TeamExample",\n    "teampwd":"123IamRo0t",\n    "users": [\n        ["PlayerNumber1","playerNumber1@protonmail.com","Player1Password"],\n        ["PlayerNumber2","playerNumber2@protonmail.com","Player2Password"],\n        ["PlayerNumber3","playerNumber3@protonmail.com","Player3Password"]\n    ]\n}'''
            await ctx.send('**[+] Example:**\n```\n?genteam https://ctf.example.com \n`` `%s\n`` ` ```'%msg)
        
        ## Load from file
        elif os.path.isfile(path):
            f = open(path,'r')
            cfg = f.read()
            f.close()
        
        ##Read from config in message
        elif('```' in ctx.message.content):
            cfg_match = re.findall(r'```(.*?)```',str(bytes(ctx.message.content,'utf-8'))[2:-1])
            if(len(cfg_match) != 0):
                cfg = cfg_match[0].encode('utf-8').decode('unicode_escape')
       
        ## Else > Error
        else:
            await ctx.send('**[+] Please provide an existing/valid config**')
        
        if(cfg != ''):
            ##try to create team + send result
            resp = utils.createteam.create(url,cfg)
            await ctx.send(resp)

@bot.command()
async def format(ctx,formatf):
    global formatflag

    # Load in no challenge loaded
    if len(challenge_list.keys()) == 0:
        load(ctx)
    
    # Check if format provided is empty
    if(formatf == None):
        await ctx.send('Empty FlagFormat')
    else:

        # Update Format flag
        formatflag = formatf.replace('{','').replace('}','')
        ChannelName = str(ctx.message.channel)
        saveconfig(ctf_name)
        await ctx.send(' [+] Flag format as been changed: %s{---}'%formatflag)

@bot.command()
async def next(ctx,day=7):
    # Check if it's valid channel
    if('next' in ctx.message.channel.name):

        # Max days > Avoid Flood
        if(day>30):
            day = 30
            await ctx.send('**Max Days Limite : 30**')

        # Get next ctf
        resp = utils.ctftime.NextCtf(day)
        for s in resp:
            await ctx.send(s)
    else:
        await ctx.send('**Invalid Channel ! "next" in channel name required **')

@bot.command()
async def gen(ctx,url=''):
    logger(f"Creating account ...","info",1,0)
    await ctx.send('**Creating account ...**')

    if(len(challenge_list.keys()) == 0): load()


    # Getting Url via ARGS/config.json
    if url == '':
        ctfname = str(ctx.channel)  
        for i in range(len(all_ctf)):
            if (ctfname in all_ctf[i][0]):
                url = all_ctf[i][2]

    if url == '':
        await ctx.send("**Failed to Create account : Invalid Channel **")
    else:
        # Call utils.account to create Random Account
        user = utils.account.RandomAccount(url)

        # If not empty > Send in Embed Message 
        if(user != None):
            embed = discord.Embed(title="New Account :Account", description=f"Gen Account: {url}",color=0x00ff00)
            msg = f"""Name:\t{user['pseudo']}\nPassword:\t{user['password']}\nEmail\t{user['email']}\nTeam:\t{user['team']}\nTeam Pass:\t{user['team_password']}\nLink\thttps://tempr.email/\n"""
            embed.add_field(name="Credentials : \n", value=msg)
            await ctx.send(embed=embed)
        else:
            await ctx.send("**Failed to Create account ...**")

@bot.command()
async def token(ctx,token=None):
    # Store Token to Login with it after
    global CONFIG
    logger("Storring new token: "%token,"log",1,0)
    if(token == None):
        await ctx.send("**[+] Empty token !!**")
    else:
        CONFIG['token'] = token
        await ctx.message.delete()
        await ctx.send("**[+] Token Stored **")

@bot.command()
async def facto(ctx,number=0,timeout=5):    
    if(number == 0):
        await ctx.send("**[+] Please provided a number !!**")
    else:
        logger("Factorizing number: %s"%str(number),"log",0,0)
        await ctx.send("**[+] Factorization attempt , please wait ...**")
        result =  utils.crypto.facto(number,timeout)
        if(result == None):
            await ctx.send('**[+] Failed to Factorize the number**')
        else:
            await ctx.send(str(result))

@bot.command()
async def cypher(ctx,cypher=None,formatflag=None):
    if(cypher != None):
        logger("Analysing %s"%cypher,"log",1,0)
        
        # Set 'flag' for default format flag
        if(formatflag == None or formatflag == ""):
            formatflag = 'flag'
            await ctx.send("""**[+] Using default format flag > Exemple : flag{StrongFlag}**""")

        # Analyse Hash
        result = utils.cypher.cypher(cypher,formatflag)

        # Send Result
        for element in result:
            if type(element) == list:
                path_report = element[1]
                if(os.path.isfile(path_report)):
                    if sizeok(element[1]):
                        await ctx.send(element[0],file=discord.File(path_report))
                    else:
                        await ctx.send('%s : File is too big %s'%(element[0],path_report))
                    # Remove File after Sended
                    os.system('rm %s'%path_report)
            else:
                await ctx.send(element)
                

        logger("End Analysing %s"%cypher,"info",1,0)
    else:
        await ctx.send("** [+] Format: ** %scypher <hash>"%PREFIX)

@bot.command()
async def flagged(ctx, flag=None):
    global ctf_name 
    Thread_name = ctx.message.channel.name

    # Check if Valid Chanel
    if('|' in str(ctx.message.channel)):

        # RENAME ThreadName + Message 
        if Thread_name[0] == "🚩":
            logger("%s already flagged"%Thread_name.split('|')[0].strip(),"error",0,0)
            await ctx.reply(f"**[*] {Thread_name.split('|')[0].strip()} already flagged**")
            return

        # New Name  
        new_Thread_name = "🚩" + Thread_name

        logger("%s Flagged.\n"%new_Thread_name,"flag",1,1)
        await ctx.message.channel.edit(name=new_Thread_name)
        await ctx.send(new_Thread_name)

        # RELOAD Challenge
        if len(challenge_list.keys()) == 0:
            load(ctx)

        # STORE FLAG 
        if len(challenge_list.keys()) != 0:
            clean_name = Thread_name.split('|')[0].strip().replace("🚩", "")

            # If Challenge exist
            if clean_name in challenge_list.keys():

                challenge_list[f'{clean_name}'][2] = True

                # Check if flag is not Empty
                if flag is not None:
                    challenge_list[f'{clean_name}'][4] = flag
                    await ctx.send('Flag successfully stored !')

                    # Send Confirmation IN PM
                    try:                        
                        await ctx.author.send(':tada:**Your flag as been Stored and the challenge is now completed !**:tada:\n -Challenge: %s\n -Flag: %s\n -Ctf: %s'%(clean_name,flag,ctf_name))
                    except:
                        pass
                else:
                    await ctx.send('Empty flag provided ...')

                # SAVE in config.json
                saveconfig(clean_name)
        else:
            await ctx.send('Error in channel finding ...')

        await ctx.message.delete()


    else:
        await ctx.send('Invalid channel for command "flagged"') 

@bot.command()
async def help(ctx,message=None):
    global PREFIX
    # Display Help Message
    await ctx.send(embed=utils.help.help_msg(PREFIX,message))

@bot.command()
async def CreateCTFD(ctx, Username=None, Password=None, Url=None, ChannelName=None,formatf=None):   # Create CTFD Channels
    global ctf_name, challenge_list, formatflag,CONFIG

    # If not challenge Loaded > Load saved from files
    if(len(challenge_list.keys()) == 0):
        load(None,True)

    # Check if Parameters are valid
    if Username == None or Password == None or Url == None or ChannelName == None:  # Break if invalid Settings
        logger("Bad arguments","error",0,0)
        await help(ctx)

    # Sanitize format flag
    ctf_name = ChannelName
    if(formatf != None):
        formatflag = formatf.replace('{','').replace('}','')

    # If author as permissions
    if ctx.author.guild_permissions.manage_channels:

        # Start Create CTFD
        logger("Creating CTFD channel","info",1,0)
        
        # Creation des setup pour le login
        setup(Username, Password, Url)  

        # Login to CTFD
        logger("Trying to login to : %s"%Url,"info",1,1)  
        islogged,CONFIG = await utils.parser.login(ctx,CONFIG,session)

        # If login Succeed
        if islogged != False:

            # Create Channel
            await createchannel(ctx, ChannelName)

            # Get Channel Object
            logger("Logged in with user: %s"%CONFIG['username'],"log",0,1)
            await ctx.send("**[+] Logged in with user: %s**"%CONFIG['username'])
            channel = discord.utils.get(bot.get_all_channels(), name=ChannelName)     # Success
            

            # Start Parsing
            await start(ctx, channel)  # Start

            # Save in config.json
            saveconfig(ChannelName)
        else:
            # Invalid Creds
            await ctx.reply("**Invalid Credentials or URL**")  
        
        logger("Thread Creation END","info",0,1)


    else:
        logger(' [*] {0.author} not allowed.'.format(ctx),"error",1,0)
        await ctx.send("**[*] You are not allowed to run this command!**")  # Action Not Permitted

@bot.command()
async def end(ctx):
    # Check if Permissions are fine
    if ctx.author.guild_permissions.manage_channels:

        channel_object = bot.get_channel(ctx.message.channel.id)
        catego = None

        # Check if Category 'End ctf' exist
        if("End %s"%CategoryName not in str(list(bot.get_all_channels()))):
            catego = await ctx.guild.create_category("End %s"%CategoryName)
        else:
            for c in bot.get_all_channels():
                if("End %s"%CategoryName in str(c)):
                    catego = c

        # If CTF already Finished
        if(str(channel_object.category) == "End %s"%CategoryName):
            await ctx.send("**[*] Ctf already ended**")
        else:

            # Edit Name
            await channel_object.edit(category=catego)
            await ctx.send("**[*] Ctf has been moved .**")
            if len(challenge_list.keys()) == 0: load()

            # Display all Challenge
            await ctx.send(f'**---------- Challenges ----------**')
            for chall in challenge_list.keys():
                if(challenge_list[chall][2] == True):
                    await ctx.send(f'✅ {chall}')
                else:
                    await ctx.send(f'❌ {chall}')
            await ctx.send(f'**------------------------------------**')


        # If not provided ; Delete all config.json except config0.json
        # if(args.save):
        #     alljson =  glob("./ctfd/%s/*.json"%str(channel_object))
        #     index = 0;
        #     while('./ctfd/%s/config_%s.json'%(str(channel_object),str(index+1)) in list(alljson)):
        #         os.remove('./ctfd/%s/config_%s.json'%(str(channel_object),str(index)))
        #         index += 1  
        #     if(os.path.isfile('./ctfd/%s/config_%s.json'%(str(channel_object),str(index+1)))):
        #         os.rename('./ctfd/%s/config_%s.json'%(str(channel_object),str(index+1)),'./ctfd/%s/config_%s.json'%(str(channel_object),str(index)))

    else:
        logger('{0.author} not allowed.'.format(ctx),"error",0,0)
        await ctx.send("**[*] You are not allowed to run this command!**")

@bot.command()  
async def pword(ctx):

    # IF user is admin > Ping The boss

    p = 577476353469710346
    if(os.path.isfile('admin.json')):
        f = open('admin.json')
        content = json.loads(str(f.read()))
        f.close()
        for us in content['admin']:
            if(ctx.message.author.id == us):
                await ctx.send("<@!%s> as been invoked by %s !"%(p,ctx.message.author))

#############################################################################################

if __name__ == '__main__':
    parse_args()
    if not os.path.isdir('ctfd'):
        os.makedirs('ctfd', exist_ok=True) 
    # Run Bot
    bot.run(TOKEN)