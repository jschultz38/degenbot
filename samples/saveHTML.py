import requests
from bs4 import BeautifulSoup
import re

URL = 'https://krakenhockeyleague.com/suspensions'
page = requests.get(URL)

with open("temp.txt", "wb") as f:
    f.write(page.content)
print('done')

with open("temp.txt", "rb") as f:
    content = f.read()
    soup = BeautifulSoup(content, "html.parser")
    results = soup.css.select('a[href*="/suspensions/?season="]')
    l = []
    for result in results:
        season = result['href'].split("=")[-1]
        if season not in l:
            l.append(season)
        if ('2121' in result['href']):
            print(result.prettify())
    print(l)
print('done')
