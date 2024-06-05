import requests
from bs4 import BeautifulSoup
import re

URL = 'https://krakenhockeyleague.com/team/9938/schedule/?season=2118'
page = requests.get(URL)

#with open("sampleHTML.txt", "wb") as f:
#	f.write(page.content)
#print('done')

with open("sampleHTML.txt", "rb") as f:
	content = f.read()
	soup = BeautifulSoup(content, "html.parser")
	print(soup)
print('done')