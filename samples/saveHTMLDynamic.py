import requests
from bs4 import BeautifulSoup
import re
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


URL = 'https://snokingpondhockey.com/#/home/schedule/1097/0/3320'
options = Options()
options.add_argument('--headless=new')
driver = webdriver.Chrome(options=options)
driver.get(URL)
import time
time.sleep(5)

html = driver.page_source
soup = BeautifulSoup(html, "html.parser")


with open("sampleHTMLPond.txt", "w") as f:
	f.write(soup.prettify())
print('done')

#with open("sampleHTML.txt", "rb") as f:
#	content = f.read()
#	soup = BeautifulSoup(content, "html.parser")
#	print(soup)
#print('done')
