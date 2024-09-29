import datetime
import traceback

from fetch.khl import fetchKHLGames, fetchKHLSuspensions
from fetch.stackeddeck import fetchSDGames
from fetch.pride import fetchPrideGames
from fetch.pond import fetchPondGames
from fetch.aahl import fetchAAHLGames
from fetch.sjha import fetchSJHAGames
from globals import TEST_MODE, CACHING_LOCK


def retrieveAllGames(team_data, player, sort=True):
    teams = team_data['teams']
    '''Just acquire the lock at the beginning since we don't
    need cache.py mucking around while we are trying to answer a request'''
    CACHING_LOCK.acquire()
    games = []

    # Obtain games
    if TEST_MODE:
        # TODO: Make this better
        addTeamGames(games, teams[0], team_data['seasons'])
    elif player is None:
        for team in teams:
            addTeamGames(games, team, team_data['seasons'])
    else:
        for team in teams:
            if playerInList(player, team['players']):
                addTeamGames(games, team, team_data['seasons'])

    if sort:
        games.sort(key=lambda e: e.gametime)

    CACHING_LOCK.release()

    return games


def playerInList(target, players):
    for player in players:
        if target.lower() in player.lower():
            return True
    return False


'''MUST aqcuire CACHING_LOCK before calling this method'''


def addTeamGames(games, team, seasons):
    found_games = []

    try:
        match team['league']:
            case 'KHL':
                print("KHL")
                found_games = fetchKHLGames(team, seasons)
            case 'SD':
                print("SD")
                found_games = fetchSDGames(team)
            case 'Pride':
                print("Pride")
                found_games = fetchPrideGames(team)
            case 'SKAHL Pond':
                print("SKAHL Pond")
                found_games = fetchPondGames(team)
            case 'AAHL':
                print("AAHL")
                found_games = fetchAAHLGames(team)
            case 'SJHA':
                print("SJHA")
                found_games = fetchSJHAGames(team)
            case _:
                raise Exception(
                    "ERROR: Could not find league <" + team['league'] + ">")
    except Exception as e:
        error_message = "ERROR: Exception while retrieving games in " + \
            team['league'] + "\n" + traceback.format_exc()
        print(error_message)
        with open("logs/error.log", "a") as errorfile:
            errorfile.write(str(datetime.date.today()) +
                            ": " + error_message + "\n\n")

        return

    games += found_games


def retrieveSuspensions(team_data, player):
    print("KHL sus")
    suss = fetchKHLSuspensions(team_data)
    if player:
        return [s for s in suss if str(player.lower()) in str(s.name.lower())]
    else:
        return suss
