import requests
import json
import re

#Get website version
URL = 'https://snokinghockeyleague.com/'
page = requests.get(URL)
text = page.content.decode('utf-8')
version = re.search('meta name="version" content="(\\d+)"', text).groups()[0]
print('The current version is ' + version)


# Get season id
URL = f'https://snokingpondhockey.com/api/season/all/0?v={version}'
page = requests.get(URL)
json_str = page.content.decode('utf8')#.replace("'", '"')
j = json.loads(json_str)
print('current season id is ' + str(j['seasons'][0]['id']))