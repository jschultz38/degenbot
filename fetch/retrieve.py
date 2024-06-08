import datetime

from fetch.khl import fetchKHLGames
from fetch.pridetourney import fetchPrideTourneyGames
from fetch.stackeddeck import fetchSDGames
from fetch.pride import fetchPrideGames
from globals import RATE_LIMITED

def retrieveAllGames(teams, player, sort=True):
    games = []

    # Obtain games
    if RATE_LIMITED:
        #TODO: Make this better
        addTeamGames(games, teams[0])
    elif player == None:
        for team in teams:
            addTeamGames(games, team)
    else:
        for team in teams:
            if playerInList(player, team['players']):
                addTeamGames(games, team)

    if sort:
        games.sort(key=lambda e: e.gametime)

    return games

def playerInList(target, players):
    for player in players:
        if target.lower() in player.lower():
            return True
    return False

def addTeamGames(games, team):
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
        case 'SPC':
            print("SPC")
            found_games = fetchPrideTourneyGames(team)
        case _:
            print("ERROR: Could not find league <" + team['league'] + ">")

    games += found_games
