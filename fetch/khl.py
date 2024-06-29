import requests
from bs4 import BeautifulSoup
import datetime
import urllib.parse as urlparse

from globals import TEST_MODE
from fetch.common.sportzone import createSportZoneGame
from utils.player import Suspension

def fetchKHLGames(team):
    page = None
    soup = None
    games = []

    if 'cache' in team:
        content_cache = team['cache']
        print('found cache')
        return team['cache']

    if not TEST_MODE:
        KHL_BASE_URL = "https://krakenhockeyleague.com/"
        URL = f'{KHL_BASE_URL}team/{team['id']}/schedule'
        #URL = f'https://krakenhockeyleague.com/ical/{team["id"]}'
        print(URL)
        page = requests.get(URL)
        if page.status_code != 200:
            print('ERROR: Could not retrieve website: ' + str(page.reason) + ", " + str(page.status_code))
            return games
        soup = BeautifulSoup(page.content, "html.parser")
    else:
        print("rate limited, opening sample file")
        with open("samples/sampleKHLHTML.txt", 'rb') as sample_file:
            content = sample_file.read()
            soup = BeautifulSoup(content, "html.parser")
    #find the image in the KHL site, then parse the url and encode any odd characters, then replace the placeholder image in the teams object.
    image = soup.find('img', attrs={'class': 'float-left'})
    image_url = urlparse.quote(image['src'])
    team['logo_url'] = f"{KHL_BASE_URL}{image_url}"

    tables = soup.find_all('table', attrs={'class':'display table table-striped border-bottom text-muted table-fixed'})
    for table in tables:
        table_body = table.find('tbody')
        rows = table_body.find_all('tr')
        
        for row in rows:
            cols = row.find_all('td')

            # khl uses sz backed website
            game = createSportZoneGame(cols, team)
            games.append(game)

    team['cache'] = games

    return games

def fetchKHLSuspensions(khl_seasons):
    if TEST_MODE:
        return []

    if 'current_seasons_cache' in khl_seasons:
        print('found current seasons in cache')
        return khl_seasons['current_seasons_cache'] + khl_seasons['past_seasons_cache']

    suss = []
    base_URL = 'https://krakenhockeyleague.com/suspensions/?season='
    for season in khl_seasons['current_seasons']:
        URL = base_URL + str(season)
        print(URL)
        page = requests.get(URL)
        if page.status_code != 200:
            print('ERROR: Could not retrieve website: ' + str(page.reason) + ", " + str(page.status_code))
            continue
        soup = BeautifulSoup(page.content, "html.parser")

        tables = soup.find_all('table', attrs={'class':'table border-bottom table-striped text-muted order-column table-responsive-md'})
        for table in tables:
            rows = table.find('tbody').find_all('tr')

            for row in rows:
                cols = row.find_all('td')

                sus_date = datetime.datetime.strptime(cols[0].getText(), "%b %d, %Y")
                sus_name = cols[1].a.getText()
                sus_team = cols[2].a.getText()
                sus_div = cols[3].getText()
                sus_games = int(cols[4].getText())
                sus_id = cols[5].a.get('href').split('/')[2]
                sus_link = 'https://krakenhockeyleague.com/suspension-details/' + sus_id

                sus = Suspension(sus_date, sus_name, sus_team, sus_div, sus_games, sus_id)
                suss.append(sus)

    khl_seasons['current_seasons_cache'] = suss
    return suss + khl_seasons['past_seasons_cache']
