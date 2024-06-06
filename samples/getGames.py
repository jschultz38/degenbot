import requests
from bs4 import BeautifulSoup
import re

URL = 'https://krakenhockeyleague.com/team/9938/schedule/?season=2118'
page = requests.get(URL)

soup = BeautifulSoup(page.content, "html.parser")

tables = soup.find_all('table', attrs={'class':'display table table-striped border-bottom text-muted table-fixed'})
print(len(tables))

games = []

for table in tables:
    table_body = table.find('tbody')
    rows = table_body.find_all('tr')

    for row in rows:
        cols = row.find_all('td')

        def myGetText(element):
            return element.getText()

        #diff return based on if game has results yet
        if ("Preview" in cols[-1].getText()):
            games.append(", ".join(map(myGetText, cols[1:-3:])))
        else:
            games.append(", ".join(map(myGetText, cols[1:-1:])))


for g in games:
    print(g)
