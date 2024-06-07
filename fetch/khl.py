import requests
from bs4 import BeautifulSoup

from fetch.SportZone import createSportZoneGame
from globals import RATE_LIMITED


def fetchKHLGames(team):
    page = None
    soup = None
    games = []

    if 'cache' in team:
        content_cache = team['cache']
        print('found cache')
        soup = BeautifulSoup(content_cache, "html.parser")
    elif not RATE_LIMITED:
        URL = 'https://krakenhockeyleague.com/team/' + team['id'] + '/schedule'
        print(URL)
        page = requests.get(URL)
        if page.status_code != 200:
            print('ERROR: Could not retrieve website: ' + page.reason + ", " + page.status_code)
            return
        team['cache'] = page.content
        soup = BeautifulSoup(page.content, "html.parser")        
    else:
        print("rate limited, opening sample file")
        with open("samples/sampleKHLHTML.txt", 'rb') as sample_file:
            content = sample_file.read()
            team['cache'] = content
            soup = BeautifulSoup(content, "html.parser")
    
    tables = soup.find_all('table', attrs={'class':'display table table-striped border-bottom text-muted table-fixed'})
    for table in tables:
        table_body = table.find('tbody')
        rows = table_body.find_all('tr')
        
        for row in rows:
            cols = row.find_all('td')

            # khl uses sz backed website
            game = createSportZoneGame(cols, team)
            games.append(game)

    return games
