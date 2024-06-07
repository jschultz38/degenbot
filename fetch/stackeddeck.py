import requests
import datetime
from game import HockeyGame
from globals import RATE_LIMITED
from bs4 import BeautifulSoup
from res.livebarn import construct_gameurl

def fetchSDGames(team):
    if RATE_LIMITED:
        return []

    page = None
    soup = None
    games = []

    if 'cache' in team:
        content_cache = team['cache']
        print('found cache')
        soup = BeautifulSoup(content_cache, "html.parser")
    else:
        URL = 'https://www.mystatsonline.com/hockey/visitor/league/schedule_scores/schedule.aspx?IDLeague=64338'
        page = requests.get(URL)
        if page.status_code != 200:
            print('ERROR: Could not retrieve website: ' + page.reason + ", " + page.status_code)
            return
        team['cache'] = page.content
        soup = BeautifulSoup(page.content, "html.parser")
    
    table = soup.find('table', attrs={'id':'maincontent_gvGameList'})
    table_body = table.find('tbody')
    rows = table_body.find_all('tr')

    x = 0
    dateText = None
    cur_month_int = None
    cur_month_descriptive = None
    cur_day_int = None
    cur_day_descriptive = None
    while x < len(rows):
        row = rows[x]

        # Case 1: Row is an empy placeholder
        if row.has_attr('class') and row['class'][0] == "dontprint":
            x += 1
            continue
        
        # Case 2: Row is date separator
        if row.has_attr('class') and row['class'][0] == "tableScheduleSeparator":
            dateText = row.td.span.getText().split(" ")

            cur_month_descriptive = dateText[1]
            match dateText[1]:
                case 'April':
                    cur_month_int = 4
                case 'May':
                    cur_month_int = 5
                case 'June':
                    cur_month_int = 6
                case 'July':
                    cur_month_int = 7
                case 'August':
                    cur_month_int = 8
                case _:
                    print("ERROR: Could not translate month in SD")
            cur_day_int = int(dateText[2].split(",")[0])
            cur_day_descriptive = dateText[0]

            x += 1
            continue

        # Case 3: Row is a game
        game = createSDGame(team, row, cur_month_int, cur_month_descriptive, cur_day_int, cur_day_descriptive)
        if game:
            print(game)
            games.append(game)

        x += 1

    return games

def createSDGame(team, row, cur_month_int, cur_month_descriptive, cur_day_int, cur_day_descriptive):
    cols = row.find_all('td')

    ## Get teams
    away_team = cols[1].a.div.getText().split(" ")[0]
    home_team = cols[5].a.find('div', attrs={'style':'display:inline-block;padding:0 10px 0 0;'}).getText().split(" ")[0]

    if team['id'] != away_team and team['id'] != home_team:
        return None

    ## Get game time
    hour = int(cols[0].span.a.getText().split(":")[0])
    minute_text = cols[0].span.a.getText().split(":")[1].split(" ")[0]
    meridiem = cols[0].span.a.getText().split(":")[1].split(" ")[1][:2]
    gametime = datetime.datetime(2024, cur_month_int, cur_day_int, hour=hour if meridiem == "AM" else hour+12, minute=int(minute_text))    

    ## Get location
    location = cols[6].getText().strip()

    # Create livebarn URL
    gameurl = construct_gameurl(location)

    ## Get Away/Home (the side of the rink)
    side = "HOME" if team['id'] == home_team else "AWAY"

    ## Check if results have been posted for the game
    away_score = None
    home_score = None
    result = None
    if '-' not in cols[2].getText():
        ### Get score
        away_score = int(cols[2].getText())
        home_score = int(cols[4].getText())

        ### Get W/L
        if home_score == away_score:
            result = 'T'
        elif (side == 'HOME' and home_score > away_score) or (side == 'AWAY' and home_score < away_score):
            result = 'W'
        else:
            result = 'L'


    ## Create string repr
    string_repr = "" + cur_day_descriptive + ", " + \
                    cur_month_descriptive + " " + str(cur_day_int) + ", " + \
                    str(hour) + ":" + minute_text + " " + meridiem + ", " + \
                    location + ", " + \
                    side + ", "

    if result != None:
        if side == 'HOME':
            string_repr += result + ", " + \
                            home_score + " - " + str(away_score) + ", "
        else:
            string_repr += result + ", " + \
                            str(away_score) + " - " + str(home_score) + ", "

    if side == 'HOME':
        string_repr += "^" + home_team + " vs " + away_team
    else:
        string_repr += "^" + away_team + " vs " + home_team
    game = HockeyGame(team, string_repr, gametime, gameurl)

    return game
