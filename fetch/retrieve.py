import datetime

from fetch.khl import fetchKHLGames
from fetch.stackeddeck import fetchSDGames
from fetch.pride import fetchPrideGames
from globals import RATE_LIMITED

def retrieveAllGames(teams, player, onlyUpcoming, onlySoon):
    games = []

    # Obtain games
    if RATE_LIMITED:
        #TODO: Make this better
        addTeamGames(games, teams[0], onlyUpcoming, onlySoon)
    elif player == None:
        for team in teams:
            addTeamGames(games, team, onlyUpcoming, onlySoon)
    else:
        for team in teams:
            if playerInList(player, team['players']):
                addTeamGames(games, team, onlyUpcoming, onlySoon)

    # Sort games before returning to user
    games.sort(key=lambda e: e.gametime)

    return games

def playerInList(target, players):
    for player in players:
        if target.lower() in player.lower():
            return True
    return False

def addTeamGames(games, team, onlyUpcoming, onlySoon):
    # Fetch games
    match team['league']:
        case 'KHL':
            print("KHL")
            found_games = fetchKHLGames(team)
        case 'SD':
            print("SD")
            found_games = fetchSDGames(team)
        case 'Pride':
            print("Pride")
            found_games = fetchPrideGames(team)
        case _:
            print("ERROR: Could not find league <" + team['league'] + ">")

    # Append wanted games
    time_now = datetime.datetime.now()
    today = datetime.datetime(time_now.year, time_now.month, time_now.day)
    for game in found_games:
        if onlySoon:
            if game.gametime > today and (game.gametime - today) < datetime.timedelta(days=7):
                games.append(game)
        elif game.gametime > today or not onlyUpcoming:
            games.append(game)
