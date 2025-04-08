import requests
from bs4 import BeautifulSoup
import datetime
import urllib.parse as urlparse
import time
from requests_html import HTMLSession

from globals import TEST_MODE
from fetch.common.sportzone import createSportZoneGame
from utils.common import selenium_retrieve_website_data
from utils.player import Suspension


def fetchKHLGames(team, seasons):
    page = None
    soup = None
    games = []

    if 'cache' in team:
        content_cache = team['cache']
        print('found cache')
        return team['cache']

    if not TEST_MODE:
        soups = []
        for season in seasons['khl']['current_seasons']:
            KHL_BASE_URL = "https://krakenhockeyleague.com/"
            URL = f'{KHL_BASE_URL}team/{team["id"]}/schedule/?season=' + str(
                season)
            print(f"Finding Game data for {URL}")
            try:
                page = requests.get(URL)
                page_content = page.content
                page.raise_for_status()
            except requests.exceptions.RequestException as e:
                print(f'ERROR: Could not retrieve website: {e}')
                try:
                    print("Attempting with Selenium...")
                    page_content = selenium_retrieve_website_data(URL)
                except Exception as selenium_error:
                    print(f'Selenium also failed: {selenium_error}')
                    return
            soups.append(BeautifulSoup(page_content, "html.parser"))

        '''Update the logo_url

        - find the image in the KHL site
        - parse the url and encode any odd characters
        - replace the placeholder image in the teams object.'''
        image = soups[0].find('img', attrs={'class': 'float-left'})
        image_url = urlparse.quote(image['src'])
        team['logo_url'] = f"{KHL_BASE_URL}{image_url}"
        print(f"Updated logo_url to <{team['logo_url']}>")
    else:
        print("rate limited, opening sample file")
        with open("samples/sampleKHLHTML.txt", 'rb') as sample_file:
            content = sample_file.read()
            soup = BeautifulSoup(content, "html.parser")

    for soup in soups:
        #Finds the Months to be able to identify each table of games
        try:
            headings = soup.find_all('h1', attrs={
                                   'class': 'text-primary p2 text-uppercase mb-3 mt-4'})
            #For Sportzone game schedules are broken into tables under each month
            tables = soup.find_all('table',
                                   class_="display table table-striped border-bottom text-muted table-fixed dataTable no-footer")
            # Extract and print table data, fails more gracefully
            for table in tables:
                table_body = table.find("tbody")
                if not table_body:
                    continue

                rows = table_body.find_all("tr")

                #iterates through the schedule table by row and pulls each column into a list
                for heading, row in zip(headings, rows):
                    cols = row.find_all("td")
                    game = createSportZoneGame(cols, team, heading=heading)
                    games.append(game)
            team['cache'] = games
        except Exception as e:
            print(f"There was an issue getting game data: {e}")

    return games


def fetchKHLSuspensions(team_data):
    if TEST_MODE:
        return []

    suspensions = team_data['suspensions']['khl']

    all_suspensions = []
    base_URL = 'https://krakenhockeyleague.com/suspensions/?season='
    cache_found = False
    for season, value in suspensions.items():
        if 'cache' in value:
            all_suspensions += value['cache']
            cache_found = True
            continue

        season_suspensions = []
        URL = base_URL + str(season)
        print(URL)

        page = requests.get(URL)
        if page.status_code != 200:
            print('ERROR: Could not retrieve website: ' +
                  str(page.reason) + ", " + str(page.status_code))
            continue
        soup = BeautifulSoup(page.content, "html.parser")

        tables = soup.find_all('table', attrs={
                               'class': 'table border-bottom table-striped text-muted order-column table-responsive-md'})
        for table in tables:
            rows = table.find('tbody').find_all('tr')

            for row in rows:
                cols = row.find_all('td')

                sus_date = datetime.datetime.strptime(
                    cols[0].getText(), "%b %d, %Y")
                sus_name = cols[1].a.getText()
                sus_team = cols[2].a.getText()
                sus_div = cols[3].getText()
                sus_games = int(cols[4].getText())
                sus_id = cols[5].a.get('href').split('/')[2]
                sus_link = 'https://krakenhockeyleague.com/suspension-details/' + sus_id

                sus = Suspension(sus_date, sus_name, sus_team,
                                 sus_div, sus_games, sus_id)
                season_suspensions.append(sus)
        suspensions[season]['cache'] = season_suspensions
        all_suspensions += season_suspensions

        # In case we are loading a lot, don't want to overload
        time.sleep(1)

    if cache_found:
        print("cache found")

    return all_suspensions
