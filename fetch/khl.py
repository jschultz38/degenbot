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
    # Create textual representation
    cols_text = None
    if ("Preview" in cols[-1].getText()):
        opponent = cols[-4].getText()
        cols_text = ", ".join(map(lambda e: e.getText(), cols[1:-4:]))
        cols_text += ", ^" + team['name'] + " vs " + opponent
    else:
        opponent = cols.pop(5).getText()
        cols_text = ", ".join(map(lambda e: e.getText(), cols[1:-1:]))
        cols_text += ", ^" + team['name'] + " vs " + opponent
    textual_rep = cols_text

    # Find game time
    dateText = cols[1].getText()
    timeText = cols[2].getText()

    ## Get day
    day_ret = int(dateText.split(" ")[2])

    ## Get month
    month_text = dateText.split(" ")[1]
    month_ret = None

    match month_text:
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
    month_ret = int(month_ret)

    ## Get time
    hour = timeText.split(":")[0]
    minute = timeText.split(":")[1].split(" ")[0]
    meridiem = timeText.split(":")[1].split(" ")[1]

    hour_ret = int(hour) if meridiem == "AM" else int(hour) + 12
    minute_ret = int(minute)

    gametime = datetime.datetime(2024, int(month_ret), int(day_ret), hour=hour_ret, minute=minute_ret)

    game = HockeyGame(team, textual_rep, gametime)
    print(game)

    return game
