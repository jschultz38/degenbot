import requests

from fetch.common.SportZone import createSportZoneGame
from globals import TEST_MODE
from bs4 import BeautifulSoup

def fetchPrideGames(team):
    if TEST_MODE:
        return []

    page = None
    soup = None
    games = []

    if 'cache' in team:
        games = team['cache']
        print('found cache')
        return games

    URL = 'https://stats.seattlepridehockey.org/team/' + team['id'] + '/schedule'
    print(URL)
    page = requests.get(URL)
    if page.status_code != 200:
        print('ERROR: Could not retrieve website: ' + str(page.reason) + ", " + str(page.status_code))
        return games
    team['cache'] = page.content
    soup = BeautifulSoup(page.content, "html.parser")

    tables = soup.find_all('table', attrs={'class':'display table table-striped border-bottom text-muted table-fixed'})

    for table in tables:
        table_body = table.find('tbody')
        rows = table_body.find_all('tr')

        for row in rows:
            cols = row.find_all('td')

            # pride league uses sz backed website
            game = createSportZoneGame(cols, team)
            games.append(game)

    team['cache'] = games

    return games
