import requests
from bs4 import BeautifulSoup
import re

URL = 'https://www.mystatsonline.com/hockey/visitor/league/schedule_scores/schedule.aspx?IDLeague=64338'
page = requests.get(URL)

with open("sampleHTMLSD.txt", "wb") as f:
	f.write(page.content)
print('done')

#with open("sampleHTML.txt", "rb") as f:
#	content = f.read()
#	soup = BeautifulSoup(content, "html.parser")
#	print(soup)
#print('done')
