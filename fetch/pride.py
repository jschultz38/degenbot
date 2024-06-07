import requests

from fetch.khl import createKHLGame
from globals import RATE_LIMITED
from bs4 import BeautifulSoup

def fetchPrideGames(team):
    if RATE_LIMITED:
        return []

    page = None
    soup = None
    games = []

    if 'cache' in team:
        content_cache = team['cache']
        print('found cache')
        soup = BeautifulSoup(content_cache, "html.parser")
    else:
        URL = 'https://stats.seattlepridehockey.org/team/' + team['id'] + '/schedule'
        print(URL)
        page = requests.get(URL)
        if page.status_code != 200:
            print('ERROR: Could not retrieve website: ' + page.reason + ", " + page.status_code)
            return
        team['cache'] = page.content
        soup = BeautifulSoup(page.content, "html.parser")

    tables = soup.find_all('table', attrs={'class':'display table table-striped border-bottom text-muted table-fixed'})

    for table in tables:
        table_body = table.find('tbody')
        rows = table_body.find_all('tr')

        for row in rows:
            cols = row.find_all('td')

            # pride league uses sportzone backed website just like khl
            game = createKHLGame(cols, team)
            games.append(game)

    return games
