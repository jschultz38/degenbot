import json

import requests
import datetime
from bs4 import BeautifulSoup

from globals import TEST_MODE
from fetch.common.sportzone import createSportZoneGame
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
    URL = (f'https://gamesheetstats.com/api/useUnifiedGames/9678'
           f'?filter[gametype]=overall'
           f'&filter[limit]=100'
           f'&filter[offset]=0'
           f'&filter[teams]={team['id']}'
           f'&filter[timeZoneOffset]=-420e')
    print(URL)
    try:
        schedule_data = json.loads(requests.get(URL).text)
        for i in range(len(schedule_data['date'])):
            game_data = {
                'location': schedule_data['location'][i],
                'details': schedule_data['details'][i],
                'date': schedule_data['date'][i],
                'home': schedule_data['home'][i],
                'visitor': schedule_data['visitor'][i],
            }
            game = createPrideGameBySchedule(game_data, team)
            if game:
                games.append(game)
        return games
    except requests.exceptions.RequestException as e:
        print(f'ERROR: Could not retrieve data: {e}')
        return games


def createPrideGameBySchedule(game_data, team):
    # Get the easy stuff
    location = game_data['location']

    # Add result-dependant variables
    away_team = game_data['visitor']['title']
    home_team = game_data['home']['title']

    if home_team != team['name'] and away_team != team['name']:
        return None
    is_degen_home = home_team == team['name']
    side = 'HOME' if is_degen_home else 'AWAY'

    # Check for a game score
    if any(c.isdigit() for c in game_data['details']) and '-' in game_data['details']:
        # This is a completed game with scores
        parts = game_data['details'].split()
        result = parts[0]  # 'W' or 'L'
        score_parts = parts[1].split('-')
        away_score = int(score_parts[0])
        home_score = int(score_parts[1])
    else:
        result = None
        home_score = None
        away_score = None

    # Get time
    gametime = datetime.datetime.strptime(game_data['date'], '%Y-%m-%dT%H:%M:%S.%fZ')

    # Create the game
    game = HockeyGame(
        team,
        gametime,
        location,
        home_team,
        away_team,
        side == 'HOME',
        home_score=home_score,
        away_score=away_score,
        result = result
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
