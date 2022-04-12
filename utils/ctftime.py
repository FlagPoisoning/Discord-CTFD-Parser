import requests
import json
from datetime import datetime,timedelta

import re

def GetCalendar(maxd):
	parameter = {
		"calendarId":"ctftime@gmail.com",
		"singleEvents":"true",
		"timeZone":"Africa/Abidjan",
		"maxAttendees":"1",
		"maxResults":"250",
		"sanitizeHtml":"true",
		"timeMin":"%sT00:00:00Z"%str(datetime.today()).split()[0],
		"timeMax":"%sT00:00:00Z"%str(datetime.now() + timedelta(days=maxd)).split()[0],
		"key":"AIzaSyBNlYH01_9Hc5S1J9vuFmu2nUqBZJNAXxs"
	}	
	try:
		return json.loads(requests.get("https://clients6.google.com/calendar/v3/calendars/%s/events"%parameter['calendarId'],params=parameter).text)
	except Exception as ex:
		return {}


def GetInfo(url):
	if(url == ""):
		return ""
	try:
		head = {"user-agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.51 Safari/537.36"}
		resp = requests.get(url,headers=head).text
		rating =  re.search(r'Rating weight: (.*?)&nbsp;',resp).group(1)
		official_url =  re.search(r'Official URL: <a href="(.*?)" rel="nofollow">',resp).group(1)
		return rating,official_url
	except Exception as ex:
		print(ex)
		return ""


def ParseJson(json_data):
	all_ = []
	for ctf in json_data["items"]:

		name  = ctf["summary"].strip()

		start = datetime.strptime(ctf["start"]["dateTime"], '%Y-%m-%dT%H:%M:%SZ').strftime("%A %d %B %Y, %H:%M UTC")
		end   = datetime.strptime(ctf["end"]["dateTime"], '%Y-%m-%dT%H:%M:%SZ').strftime("%A %d %B %Y, %H:%M UTC")

		description = ctf["description"]
		url = re.search(r'https://ctftime.org/event/(.*?)/\n',description)[0].strip()
		weight,official_url = GetInfo(url)


		info = f"```\n{'Name':<13}{': ':>4}{name}\n{'Url':<13}{': ':>4}{url}\n{'Official Url':<13}{': ':>4}{official_url}\n{'Start:' :<13}{': ':>4}{start }\n{'End':<13}{': ':>4}{end }\n{'Weight':<13}{': ':>4}{weight }\n```"
		all_.append(info)

	return all_

def NextCtf(maxd=7):
	resp = GetCalendar(maxd)
	if('error' in resp):
		return [resp["error"]["message"]]
	else:
		return ParseJson(resp)
		


#print(NextCtf())

# https://stackoverflow.com/questions/9847213/how-do-i-get-the-day-of-week-given-a-date
# import datetime
# import calendar

# day, month, year = map(int, input().split())
# my_date = datetime.date(year, month, day)
# print(calendar.day_name[my_date.weekday()])

# 08 05 2015
# Friday