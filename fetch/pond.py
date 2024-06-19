import requests
import datetime
from bs4 import BeautifulSoup

from utils.HockeyGame import HockeyGame
from globals import TEST_MODE


def fetchPondGames(team):
    if TEST_MODE:
        return []

    games = []

    if 'cache' in team:
        games = team['cache']
        print('found cache')
        return games

    '''
    1. Get website version - maybe don't care?

    "https://snokinghockeyleague.com/"
    match /meta name=\"version\"\s+content=\"(\d+)\"/

    2. BROKEN Get current season

    version = 1132170
    https://snokingpondhockey.com/api/season/all/0?v=<version>

    For some reason, this link doesn't work. no clue why because
    it works on the snoking scraping app

    3. Get teams

    season = 1097
    https://snokingpondhockey.com/api/team/list/<season>/0

    4. Get schedule for team

    pond season = 1097
    team_id = 3320
    https://snokinghockeyleague.com/api/game/list/1097/0/3320

    '''
    season = "1097"
    URL = f'https://snokinghockeyleague.com/api/game/list/{season}/0/{team["id"]}'
    print(URL)
    page = requests.get(URL)
    if page.status_code != 200:
        print('ERROR: Could not retrieve website: ' + str(page.reason) + ", " + str(page.status_code))
        return games
    soup = BeautifulSoup(page.content, "lxml")

    listed_games = eval(soup.body.p.getText().replace("null", "\"null\"").replace("false", "False"))

    for g in listed_games:
        game = createPondGame(g, team)
        games.append(game)

    team['cache'] = games

    return games

def createPondGame(game_item, team):
    gametime = datetime.datetime.strptime(game_item['dateTime'], '%Y-%m-%dT%H:%M:%S')
    location = game_item['rinkName']
    home_team = game_item['teamHomeName']
    away_team = game_item['teamAwayName']
    is_home = home_team == team['name']
    home_score = None if game_item['scoreHome'] == 'null' else int(game_item[9])
    away_score = None if game_item['scoreAway'] == 'null' else int(game_item[10])

    # Create the game
    game = HockeyGame(
                team,
                gametime,
                location,
                home_team,
                away_team,
                is_home,
                home_score=home_score,
                away_score=away_score
                )

    return game
