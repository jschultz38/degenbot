import requests
import datetime
from bs4 import BeautifulSoup

from globals import TEST_MODE
from fetch.common.sportzone import createSportZoneGame
from utils.common import selenium_retrieve_website_data
from utils.hockey_game import HockeyGame


def fetchPrideGames(team):
    if TEST_MODE:
        return []

    if 'cache' in team:
        games = team['cache']
        print('found cache')
        return games

    games = fetchPrideGamesBySchedule(team)

    team['cache'] = games
    return games


def fetchPrideGamesBySchedule(team):
    games = []
    URL = 'https://stats.seattlepridehockey.org/schedule'
    print(URL)
    try:
        page = requests.get(URL)
        page.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f'ERROR: Could not retrieve website: {e}')
        try:
            print("Attempting with Selenium...")
            page = selenium_retrieve_website_data(URL)
        except Exception as selenium_error:
            print(f'Selenium also failed: {selenium_error}')
            return

    soup = BeautifulSoup(page.content, "html.parser")
    tables = soup.find_all('table', attrs={'class': 'table text-muted mb-0'})

    for table in tables:
        rows = table.find_all('tr', attrs={'class': 'd-none d-lg-block'})

        for row in rows:
            cols = row.find_all('td')

            # pride league uses sz backed website
            game = createPrideGameBySchedule(cols, team)
            if game:
                games.append(game)

    return games


def createPrideGameBySchedule(cols, team):
    # Get the easy stuff
    location = " ".join(cols[2].getText().split(" ")[1:])[2:].strip()
    degen_team = team['name']

    # Add result-dependant variables
    cols_text = None
    away_team = None
    home_team = None
    away_score = None
    home_score = None
    if (cols[-2].a is None):
        # This is a listing for playoff games that don't have actual teams yet
        home_team = cols[3].find('span').getText()
        away_team = cols[1].find('span').getText()
    elif ("Preview" in cols[-2].a.getText()):
        home_team = cols[3].find('a', attrs={'class': 'ml-2'}).getText()
        away_team = cols[1].find('a', attrs={'class': 'mr-2'}).getText()
    else:
        # Looks like at the moment, the way I'm grabbing games does not show previous games
        print('ERROR: havent seen a scored game yet')
        return None

    if home_team != team['name'] and away_team != team['name']:
        return None
    is_degen_home = home_team == team['name']
    side = 'HOME' if is_degen_home else 'AWAY'

    # Find game time
    dateText = cols[0].getText()
    fullText = cols[2].getText().split(" ")
    timeText = fullText[0].strip() + " " + fullText[1].strip()[:2]

    # Get day
    day_ret = int(dateText.split("/")[1])

    # Get month
    month_ret = int(dateText.split("/")[0])

    # Get time
    hour = timeText.split(":")[0]
    minute = timeText.split(":")[1].split(" ")[0]
    meridiem = timeText.split(":")[1].split(" ")[1]

    hour_ret = int(hour) if meridiem == "AM" else int(hour) + 12
    minute_ret = int(minute)

    gametime = datetime.datetime(
        datetime.datetime.now().year, month_ret, day_ret, hour=hour_ret, minute=minute_ret)

    # Create the game
    game = HockeyGame(
        team,
        gametime,
        location,
        home_team,
        away_team,
        side == 'HOME',
        home_score=home_score,
        away_score=away_score
    )

    return game


''' DEPRECATED

This pulls the schedule for teams from the teams' page and it stopped working
at some point during the season so I disabled it and introduced the below code.
After reviewing it, I actually think the below code is better so I'm just
going to permanently use the other code.
'''


def fetchPrideGamesByTeam(team):
    games = []
    URL = 'https://stats.seattlepridehockey.org/team/' + \
        team['id'] + '/schedule'
    print(URL)
    page = requests.get(URL)
    if page.status_code != 200:
        print('ERROR: Could not retrieve website: ' +
              str(page.reason) + ", " + str(page.status_code))
        return games
    team['cache'] = page.content
    soup = BeautifulSoup(page.content, "html.parser")

    tables = soup.find_all('table', attrs={
                           'class': 'display table table-striped border-bottom text-muted table-fixed'})

    for table in tables:
        table_body = table.find('tbody')
        rows = table_body.find_all('tr')

        for row in rows:
            cols = row.find_all('td')

            # pride league uses sz backed website
            game = createSportZoneGame(cols, team)
            games.append(game)

    return games
