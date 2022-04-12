from typing import Generator, List, Union
import requests
from requests import Session
from requests.compat import urljoin, urlparse, urlsplit
import re
import json

import discord
from discord.ext import commands

from utils.logger import logger

async def fetch(ctx,url: str,session) -> Union[List[dict], dict]:
    res = session.get(url)
    if '{\"message' in res.text:
        msg = res.json()['message']
        await ctx.send(f'** [+] {msg}**')
    elif not res.ok or not res.json()['success']:
        logger('Failed fetching challenge!','error',1,0)
        #return []
        exit(1)
    else:
        return res.json()['data']


async def login(ctx,CONFIG,session):
    # Get in main page
    resp = requests.get(CONFIG['base_url']).text

    
    # If recaptcha Detected > Trigger 
    if('https://www.google.com/recaptcha/api.js' in resp):
        # If token stored > Login
        if CONFIG['token'] != None:

            await ctx.send('**[+] Login using token ...**')
            session.headers.update({"Content-Type": "application/json"})
            session.headers.update({"Authorization": f"Token {CONFIG['token']}"})
            resp = session.get(CONFIG['base_url']+'/api/v1/users/me').text

            # Valid token ? 
            if('success\": true' in resp):
                CONFIG['username'] = json.loads(resp)["data"]["name"]
                return True,CONFIG
            else:
                msg = json.loads(resp)["message"]
                await ctx.send(f"```\nMessage:\n{msg}```")
                return False,CONFIG
        else:
            # Help message > store the token
            logger('\nRecaptcha Detected !!\n','info',1,0)        
            await ctx.send('**[+] Recaptcha Detected !!**')
            prefix = CONFIG['PREFIX']
            await ctx.send(f'** ->  use: {prefix}token "your token"**')
            return False,CONFIG
    else:

        # If normal CTFD
        nonce = get_nonce(CONFIG,session)

        # Login
        res = session.post(
            urljoin(CONFIG['base_url'], '/login'),
            data={
                'name': CONFIG['username'],
                'password': CONFIG['password'],
                'nonce': nonce,
            }
        )

        # Keycheck
        if 'incorrect' in res.text:
            logger('Unable to Login With those credentials','error',0,1)
            return False,CONFIG
        elif 'success\": true' in session.get(CONFIG['base_url']+'/api/v1/users/me').text:
            return True,CONFIG
        else:
            return False,CONFIG

    return False,CONFIG

def get_nonce(CONFIG,session) -> str:
    # Regex to get 'nonce token' in html page
    res = session.get(urljoin(CONFIG['base_url'], '/login'))
    return re.search('name="nonce"(?:[^<>]+)?value="([0-9a-f]{64})"', res.text).group(1)

async def get_challenges(ctx,CONFIG,session):
    logger('Getting challenges ...','log',1,1)

    # Get All challenges
    challenges = await fetch(ctx,urljoin(CONFIG['base_url'], '/api/v1/challenges'),session)
    result = []

    # Get info challenge one per one
    for challenge in challenges:
        try:
            # Fetch api
            res = await fetch(ctx,urljoin(CONFIG['base_url'], f'/api/v1/challenges/{challenge["id"]}'),session)
            
            # Get Files
            file = []
            if('files' in res):
                file = res['files']

            #Other Infos  
            category = res['category']
            name = res['name'].replace(' ','_')        
            description = str(res['description']).replace('\r', '').replace('\n', '')
            points = str(res['value'])
            
            # Add all info in 'result' list
            result.append([category, name, description, points,challenge["id"],file])
        except Exception as ex:
            logger("Error during fetching/grabbing a challenge",'error',0,1)
            pass

    #return sorted(result)        
    return sorted(result)[:3]