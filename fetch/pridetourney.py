import datetime

from bs4 import BeautifulSoup
from selenium import webdriver

from game import HockeyGame
from globals import RATE_LIMITED


def fetchPrideTourneyGames(team):
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
        # such as https://my.seattlepridehockey.org/leagues/4226311/teams/6818745
        URL = 'https://my.seattlepridehockey.org/leagues/' + team['div'] + '/teams/' + team['id']
        print(URL)

        # use selenium driver because this site happens to be dynamically generated
        options = webdriver.FirefoxOptions()
        # headless is necessary otherwise it will pop up in a browser window
        options.add_argument('--headless')
        driver = webdriver.Firefox(options=options)
        driver.get(URL)
        page_html = driver.page_source

        team['cache'] = page_html
        soup = BeautifulSoup(page_html, "html.parser")

    schedule = soup.find_all('li', attrs={'class': 'schedule-game clr'})

    # for each game
    for g in schedule:
        games.append(createPrideTourneyGame(g, team))

    return games


def createPrideTourneyGame(game_html, team):
    date = game_html.find('span', attrs={'class': 'date'}).getText()
    timerange = game_html.find('span', attrs={'class': 'time'}).getText()
    start = timerange.split("-")[0].strip()

    opp = game_html.find('h3', attrs={'class': 'event-team'}).find('a').getText()
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

    gametime = datetime.datetime(2024, month_ret, day_ret, hour=hour_ret, minute=minute_ret)

    # Create the game
    game = HockeyGame(
        team,
        gametime,
        rink,
        team['name'],  # site doesn't specify home/away so default degen team as "home"
        opp,
        0
        # todo: add final scores
    )

    return game
