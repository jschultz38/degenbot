import requests
import datetime
from bs4 import BeautifulSoup

from game import HockeyGame
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

            game = createKHLGame(cols, team)
            games.append(game)

    return games

def createKHLGame(cols, team):
    # Get the easy stuff
    location = cols[3].getText()
    degen_team = team['name']
    side = cols[4].getText()
    is_degen_home = (side == "HOME")

    # Add result-dependant variables
    cols_text = None
    opponent_team = None
    away_score = None
    home_score = None
    if ("Preview" in cols[-1].getText()):
        opponent_team = cols[-4].getText()
    else:
        opponent_team = cols[5].getText()
        score_text = cols[7].getText().split(" ")
        degen_score = int(score_text[0])
        opponent_score = int(score_text[2])

        if is_degen_home:
            home_score = degen_score
            away_score = opponent_score
        else:
            home_score = opponent_score
            away_score = degen_score

    # Place teams on home/away
    if is_degen_home:
        home_team = degen_team
        away_team = opponent_team
    else:
        home_team = opponent_team
        away_team = degen_team

    # Find game time
    dateText = cols[1].getText()
    timeText = cols[2].getText()

    ## Get day
    day_ret = int(dateText.split(" ")[2])

    ## Get month
    month_text = dateText.split(" ")[1]
    month_ret = None

    match month_text:
        case 'Apr':
            month_ret = 4
        case 'May':
            month_ret = 5
        case 'Jun':
            month_ret = 6
        case 'Jul':
            month_ret = 7
        case 'Aug':
            month_ret = 8
        case 'Sep':
            month_ret = 9
        case _:
            print("ERROR: Could not decode: " + month_text)
            month_ret = 1
        
    ## Get time
    hour = timeText.split(":")[0]
    minute = timeText.split(":")[1].split(" ")[0]
    meridiem = timeText.split(":")[1].split(" ")[1]

    hour_ret = int(hour) if meridiem == "AM" else int(hour) + 12
    minute_ret = int(minute)

    gametime = datetime.datetime(2024, month_ret, day_ret, hour=hour_ret, minute=minute_ret)
    
    # Create the game
    game = HockeyGame(
                team,
                gametime,
                location,
                home_team,
                away_team,
                HockeyGame.DEGEN_HOME if is_degen_home else HockeyGame.DEGEN_AWAY,
                home_score=home_score,
                away_score=away_score
                )

    return game
