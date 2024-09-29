import requests
import datetime
from bs4 import BeautifulSoup

from globals import TEST_MODE
from utils.common import translateMonth
from utils.hockey_game import HockeyGame

def fetchSJHAGames(team):
    if TEST_MODE:
        return []

    page = None
    soup = None
    games = []

    if 'cache' in team:
        content_cache = team['cache']
        print('found cache')
        return team['cache']

    URL = f'https://www.sjha.com/schedule/team_instance/{team["id"]}'
    print(URL)
    page = requests.get(URL)
    if page.status_code != 200:
        print('ERROR: Could not retrieve website: ' +
              str(page.reason) + ", " + str(page.status_code))
        return
    soup = BeautifulSoup(page.content, "html.parser")

    table = soup.find(
        'table', attrs={'class': 'statTable sortable noSortImages'})
    table_body = table.find('tbody')
    rows = table_body.find_all('tr')

    current_year = datetime.datetime.now().year
    latest_month = datetime.datetime.now().month
    for row in rows:
        game = createSJHAGame(team, row)
        if game:
            # Handle year of the game
            if game.gametime.month < latest_month:
                current_year += 1
                latest_month = game.gametime.month
            game.gametime = game.gametime.replace(year=current_year)

            games.append(game)        

    team['cache'] = games

    return games


def createSJHAGame(team, row):
    print('==============')
    print(row.prettify())
    cols = row.find_all('td')

    # Get teams
    print(cols[2].getText().strip())
    if cols[2].getText().strip()[0] == '@':
        home_team = cols[3].getText().strip()[1:].strip()
        away_team = team['name']
        side = "AWAY"
    else:
        away_team = cols[3].getText().strip()
        home_team = team['name']
        side = "HOME"

    # Get game date and time
    date_text = cols[0].getText().strip().split(" ")
    month = translateMonth(date_text[1])
    day = int(date_text[-1])

    if cols[4].getText().strip() != 'TBD' and cols[1].getText().strip() == '-':
        time_text = cols[4].getText().strip().split(" ")
        hour = int(time_text[0].split(":")[0])
        minute = int(time_text[0].split(":")[1])
        meridiem = time_text[1]

        gametime = datetime.datetime(2024,
                                     month,
                                     day,
                                     hour=hour if meridiem == "AM" else hour + 12,
                                     minute=minute)

        # Adjust to Pacific time zone
        gametime -= datetime.timedelta(hours=3)
    else:
        '''For some reason, the website does not list the time of the game if it has already
        happened, so I don't want to bother trying to find it. Or, the game time could
        be TDB.'''
        gametime = datetime.datetime(2024, month, day)

    # Get location
    location = cols[3].getText().strip()

    # Check if results have been posted for the game
    if cols[1].getText().strip() != '-':
        score_text = cols[2].getText().strip().split(" ")[-1].split("-")
        pat_score = score_text[0]
        opp_score = score_text[1]
        home_score = pat_score if side == "HOME" else opp_score
        away_score = opp_score if side == "HOME" else pat_score
    else:
        home_score = None
        away_score = None

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
