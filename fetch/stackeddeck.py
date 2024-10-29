import requests
import datetime
from bs4 import BeautifulSoup

from globals import TEST_MODE
from utils.common import translateMonth
from utils.hockey_game import HockeyGame


def fetchSDGames(team):
    if TEST_MODE:
        return []

    page = None
    soup = None
    games = []

    if 'cache' in team:
        content_cache = team['cache']
        print('found cache')
        return team['cache']

    URL = 'https://www.mystatsonline.com/hockey/visitor/league/schedule_scores/schedule.aspx?IDLeague=64338'
    print(URL)
    page = requests.get(URL)
    if page.status_code != 200:
        print('ERROR: Could not retrieve website: ' +
              str(page.reason) + ", " + str(page.status_code))
        return
    soup = BeautifulSoup(page.content, "html.parser")

    table = soup.find('table', attrs={'id': 'maincontent_gvGameList'})
    table_body = table.find('tbody')
    rows = table_body.find_all('tr')

    x = 0
    dateText = None
    cur_month = None
    cur_day = None
    while x < len(rows):
        row = rows[x]

        # Case 1: Row is an empy placeholder
        if row.has_attr('class') and row['class'][0] == "dontprint":
            x += 1
            continue

        # Case 2: Row is date separator
        if row.has_attr('class') and row['class'][0] == "tableScheduleSeparator":
            dateText = row.td.span.getText().split(" ")

            cur_month = translateMonth(dateText[1])
            cur_day = int(dateText[2].split(",")[0])

            x += 1
            continue

        # Case 3: Row is a game
        game = createSDGame(team, row, cur_month, cur_day)
        if game:
            games.append(game)

        x += 1

    team['cache'] = games

    return games


def createSDGame(team, row, cur_month, cur_day):
    cols = row.find_all('td')

    # Get the game ID for the game and use it to build the scoresheet URL if game ID exists
    game_id=None
    score_sheet_url=None
    try:
        game_id = cols[0].contents[1].next.attrs['href'].split('(')[1].split(')')[0]
        score_sheet_url = f"https://www.mystatsonline.com/hockey/visitor/league/schedule_scores/game_score_hockey.aspx?IDLeague=64338&IDGame={game_id}"
    except Exception:
        print("Failed to get a game ID")
        pass

    # Get teams
    away_team = cols[1].a.div.getText().split(" ")[0]
    home_team = cols[5].a.find('div', attrs={
                               'style': 'display:inline-block;padding:0 10px 0 0;'}).getText().split(" ")[0]

    if team['id'] != away_team and team['id'] != home_team:
        return None

    # Get Away/Home (the side of the rink)
    side = "HOME" if team['id'] == home_team else "AWAY"

    # Get game time
    hour = int(cols[0].span.a.getText().split(":")[0])
    minute_text = cols[0].span.a.getText().split(":")[1].split(" ")[0]
    meridiem = cols[0].span.a.getText().split(":")[1].split(" ")[1][:2]
    gametime = datetime.datetime(2024,
                                 cur_month,
                                 cur_day,
                                 hour=hour if meridiem == "AM" else hour + 12,
                                 minute=int(minute_text))

    # Get location
    location = cols[6].getText().strip()

    # Check if results have been posted for the game
    away_score = None
    home_score = None
    if '-' not in cols[2].getText():
        away_score = int(cols[2].getText())
        home_score = int(cols[4].getText())

    game = HockeyGame(
        team,
        gametime,
        location,
        home_team,
        away_team,
        side == 'HOME',
        home_score=home_score,
        away_score=away_score,
        game_id=game_id,
        score_sheet_url=score_sheet_url
    )

    return game
