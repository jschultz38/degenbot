import requests
from bs4 import BeautifulSoup
import re

URL = 'https://stats.seattlepridehockey.org/schedule'
page = requests.get(URL)

with open("sampleHTMLSPT.txt", "wb") as f:
	f.write(page.content)
print('done')

#with open("sampleHTML.txt", "rb") as f:
#	content = f.read()
#	soup = BeautifulSoup(content, "html.parser")
#	print(soup)
#print('done')
