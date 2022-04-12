#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# _authors_: Vozec
# _date_ : 10/03/2022


import discord
from discord.ext import commands

def help_msg(PREFIX,message):
	embed = discord.Embed(title="Help Menu", description="",color=0x00ff00)

	embed.add_field(name='%sCreateCTFD <Username> <Password> <Url> <ChannelName>'%PREFIX,value='Create a channel + threads sorted by name',inline=False)

	embed.add_field(name='\n%sflagged ThisIsMySuperFlag (in challenge thread)'%PREFIX,value='Store the flag + renamme the challenge thread',inline=False)

	embed.add_field(name='%send (in ctfd challenge)'%PREFIX,value='Move the ctfd channel in other category',inline=False)

	embed.add_field(name='%sgen <url>'%PREFIX,value='Register a new random account on ctfd',inline=False)
	
	embed.add_field(name='%sgenteam <url> <config_path>'%PREFIX,value='Register a complete team on ctfd',inline=False)

	embed.add_field(name='%sformat <Format Flag>'%PREFIX,value='Change format flag',inline=False)

	embed.add_field(name='%scypher <hash>'%PREFIX,value='Analyse cypher provided',inline=False)

	embed.add_field(name='%sfacto <number> (optional: <timeout(min)>)'%PREFIX,value='Try to factorize the number provided',inline=False)

	embed.add_field(name='%stoken <mytoken>'%PREFIX,value='Set token account to login & bypass recaptcha',inline=False)

	embed.add_field(name='%schange'%PREFIX,value='Display menu to change the selected Ctf',inline=False)

	embed.add_field(name='%snext <days>'%PREFIX,value='Search for futurs ctf on ctftime (default days=7) ',inline=False)

	embed.add_field(name='%sanalyse (optional: <link/filename>)'%PREFIX,value='Analyse files of the selected challenges',inline=False)

	embed.add_field(name='%shelp'%PREFIX,value='Display this menu',inline=False)

	return embed
