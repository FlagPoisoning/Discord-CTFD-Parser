import utils.hashfinder
import random
import os
import subprocess
import binascii
import base64
import requests
import re
from pwn import *

from utils.other import rdnname,writefile

context.log_level = 'critical'


def execmd(cmd):
    cnt = subprocess.Popen(cmd,shell=True,stderr=subprocess.PIPE,stdout=subprocess.PIPE,stdin=subprocess.PIPE).communicate()[0].decode()
    return cnt

def append(result,command,cnt):
    if len(cnt) < 2000  and 'strings' != command:
        result.append('**%s**```\n%s```'%(command,cnt))
    else:
        rdn_name = rdnname()
        writefile('/tmp/%s.txt'%str(rdn_name),cnt)
        result.append(['**%s**'%command,'/tmp/%s.txt'%str(rdn_name)])
    return result

def clearknow(cypher,formatflag):

    final = ""  

    for k in range(len(formatflag)):

        know = k*b'_' + bytes(formatflag,'utf-8') + b'{'

        try: 
            sample_key = xor(bytes(cypher[:len(know)],'utf-8'),know)
            final += '\n> Know  (ASCII): %s | Key: %s'%(know,sample_key)
            xored     = str(xor(bytes(cypher,'utf-8'),sample_key))
            final += '\n> Xored (ASCII): %s'%(xored)
        except Exception as ex:
            final += '\n> Error (ASCII): %s'%str(ex)

        try:
            base = base64.b64decode(bytes(cypher,'utf-8'))
            sample_key = xor(base[:len(know)],know) 
            final += '\n> Know  (BASE64): %s | Key: %s'%(know,sample_key)
            xored     = str(xor(base,sample_key))
            final += '\n> Xored (BASE64): %s'%(xored)
        except Exception as ex:
            final += '\n> Error (BASE64): %s'%str(ex)

        try:
            hexa = binascii.unhexlify(bytes(cypher,'utf-8'))
            sample_key = xor(hexa[:len(know)],know)
            final += '\n> Know  (HEXA): %s | Key: %s'%(know,sample_key)
            xored     = str(xor(hexa,sample_key))
            final += '\n> Xored (HEXA): %s'%(xored)
        except Exception as ex:
            final += '\n> Error (HEXA): %s'%str(ex)

        final += "\n"

    return final

def md5decrypt(hash_,type_):
    all_ = {
        "MD5":"",
        "MD4":"Md4",
        "SHA1":"Sha1",
        "SHA256":"Sha256",
        "SHA384":"Sha384",
        "SHA512":"Sha512"
    }
    resp = requests.post("https://md5decrypt.net/%s/"%all_[type_],data={"hash":hash_,"decrypt":"Décrypter"})
    found = re.findall('%s : <b>(.*?)</b>'%hash_,resp.text.replace("\n",""))
    if(len(found) == 0):
        return '[%s] Not Found\n'%type_
    else:
        return '[%s] %s\n'%(type_,str(found))

def cypher(cypher=None,formatflag=None):

    result = []

    # Random Name + Save hash
    pathfile = '/tmp/%s.txt'%rdnname()

    writefile(pathfile,cypher)


    # Hash Finder
    cnt = utils.hashfinder.hash_finder(cypher)
    result = append(result,"Hash Finder",cnt)
    
    # List of pre-configured commands
    cmd = {
    "Strings":"timeout 10 strings -t x %s"%pathfile,
    "StringCheese":"timeout 10 stringcheese %s{ --file %s"%(formatflag,pathfile),
    "Ciphey":"timeout 10 ciphey -t '%s' -q"%cypher,
    "NameThatHash":"timeout 10 nth --text '%s' -a"%cypher,
    }

    for command in cmd.keys():
        try:
            cnt = execmd(cmd[command])
            result = append(result,command,cnt)
        except Exception as ex:
            result.append('**%s**```\n%s```'%(command,str(ex)))

    alltype = ["MD5","MD4","SHA1","SHA256","SHA384","SHA512"]
    final = ''
    for t in alltype:
        if(t in result[4]):
            try:
                final += md5decrypt(cypher,t)                
            except Exception as ex:
                final += '**Md5decrypt**```\n%s```'%str(ex)
    result = append(result,"Md5decrypt.net",final) 

    # Clear Know
    cnt = clearknow(cypher,formatflag)
    result = append(result,"Clear Know",cnt)

    return result