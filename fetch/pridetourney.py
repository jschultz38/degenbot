import requests
from bs4 import BeautifulSoup

from globals import RATE_LIMITED


def fetchPrideTourneyGames(team):
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
        # such as https://my.seattlepridehockey.org/leagues/4226311/teams/6818745
        URL = 'https://my.seattlepridehockey.org/leagues/' + team['div'] + '/teams/' + team['id']
        print(URL)
        page = requests.get(URL)
        if page.status_code != 200:
            print('ERROR: Could not retrieve website: ' + page.reason + ", " + page.status_code)
            return
        team['cache'] = page.content
        soup = BeautifulSoup(page.content, "html.parser")

        # todo extract content from the page result


    return []