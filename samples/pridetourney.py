import datetime

from bs4 import BeautifulSoup
from selenium import webdriver

from utils.hockey_game import HockeyGame
from globals import TEST_MODE

import requests
from fetch.sportzone import createSportZoneGame


def fetchPrideTourneyGames(team):
    if TEST_MODE:
        return []

    page = None
    soup = None
    games = []

    if 'cache' in team:
        content_cache = team['cache']
        print('found cache')
        soup = BeautifulSoup(content_cache, "html.parser")
    else:
        URL = 'https://stats.seattlepridehockey.org/schedule'
        print(URL)
        page = requests.get(URL)
        if page.status_code != 200:
            print('ERROR: Could not retrieve website: ' +
                  str(page.reason) + ", " + str(page.status_code))
            return games
        team['cache'] = page.content
        soup = BeautifulSoup(page.content, "html.parser")

    tables = soup.find_all('table', attrs={'class': 'table text-muted mb-0'})

    for table in tables:
        rows = table.find_all('tr', attrs={'class': 'd-none d-lg-block'})

        for row in rows:
            cols = row.find_all('td')

            # pride league uses sz backed website
            game = createPrideTourneyGame(cols, team)
            if game == None:
                continue
            games.append(game)

    return games


def createPrideTourneyGame(cols, team):
    # Get the easy stuff
    location = cols[2].a['title']
    degen_team = team['name']
    home_team = cols[1].find_all('a')[0].getText()
    away_team = cols[3].find('a', attrs={'class': 'ml-2'}).getText()

    if home_team != degen_team and away_team != degen_team:
        return None

    side = "HOME" if home_team == team['name'] else "AWAY"
    is_degen_home = (side == "HOME")

    # Find game time
    dateText = cols[0].getText().split(" ")[0]
    timeText = cols[2].getText().strip()

    # Get day
    day_ret = int(dateText.split("/")[1])

    # Get month
    month_ret = int(dateText.split("/")[0])

    # Get time
    hour = timeText.split(":")[0]
    minute = timeText.split(":")[1].split(" ")[0]
    meridiem = timeText.split(":")[1].split(" ")[1][0:2]

    hour_ret = int(hour) if meridiem == "AM" else int(hour) + 12
    minute_ret = int(minute)

    gametime = datetime.datetime(
        2024, month_ret, day_ret, hour=hour_ret, minute=minute_ret)

    # Create the game
    game = HockeyGame(
        team,
        gametime,
        location,
        home_team,
        away_team,
        HockeyGame.DEGEN_HOME if is_degen_home else HockeyGame.DEGEN_AWAY
    )

    return game


# run saveHtmlSPC.py to generate the saved files needed to run this
def fetchPrideTourneyGames2(team):
    if RATE_LIMITED:
        return []

    page_html = None
    soup = None
    games = []

    if 'cache' in team:
        content_cache = team['cache']
        print('found cache')
        soup = BeautifulSoup(content_cache, "html.parser")
    else:
        # use saved file because selenium is very slow
        file_name = "samples/saveHTMLSPC" + \
            team['name'].replace(' ', '').replace('\'', '') + ".txt"
        print("opening saved file", file_name)
        with open(file_name, 'rb') as sample_file:
            content = sample_file.read()
            team['cache'] = content
            soup = BeautifulSoup(content, "html.parser")

    schedule = soup.find_all('li', attrs={'class': 'schedule-game clr'})

    for g in schedule:
        games.append(createPrideTourneyGame2(g, team))

    return games


def createPrideTourneyGame2(game_html, team):
    date = game_html.find('span', attrs={'class': 'date'}).getText()
    timerange = game_html.find('span', attrs={'class': 'time'}).getText()
    start = timerange.split("-")[0].strip()

    opp = game_html.find(
        'h3', attrs={'class': 'event-team'}).find('a').getText()
    rink = game_html.find('p', attrs={'class': 'event-details'}).find('a').getText().replace("Kraken Community Iceplex",
                                                                                             "KCI")

    # parse date ex "Fri, Jun 7"
    day_ret = int(date.split(" ")[2])
    month_text = date.split(" ")[1]
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

    # parse start time ex "5:00 PM"
    hour = start.split(":")[0]
    minute = start.split(":")[1].split(" ")[0]
    meridiem = start.split(":")[1].split(" ")[1]

    hour_ret = int(hour) if meridiem == "AM" else int(hour) + 12
    minute_ret = int(minute)

    gametime = datetime.datetime(
        2024, month_ret, day_ret, hour=hour_ret, minute=minute_ret)

    # Create the game
    game = HockeyGame(
        team,
        gametime,
        rink,
        # site doesn't specify home/away so default degen team as "home"
        team['name'],
        opp,
        0
        # todo: add final scores
    )

    return game
