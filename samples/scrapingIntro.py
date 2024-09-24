import requests
from bs4 import BeautifulSoup
import re

URL = 'https://krakenhockeyleague.com/team/9938/schedule/?season=2118'
page = requests.get(URL)

soup = BeautifulSoup(page.content, "html.parser")

results = soup.find(id="calendar")

# print(results)

# f = open("page.txt", "w")
# f.write(str(soup))
# f.close()

results = soup.find_all("tr")


results = soup.find_all("h1", string="June 2024")


results = soup.getText()
print(soup.getText())

f = open("temp.txt", "w")
f.write(str(results))
f.close()
