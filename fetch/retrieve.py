from fetch.khl import fetchKHLGames
from globals import RATE_LIMITED

def retrieveAllGames(teams, player, onlyUpcoming, onlySoon):
    games = []

    # Obtain games
    if RATE_LIMITED:
        #TODO: In the future, make this just return 'no can do'
        games = []
        addTeamGames(games, teams[0], onlyUpcoming, onlySoon)
    elif player == None:
        games = []
        for team in teams:
            addTeamGames(games, team, onlyUpcoming, onlySoon)
    else:
        games = []
        for team in teams:
            if playerInList(player, team['players']):
                addTeamGames(games, team, onlyUpcoming, onlySoon)

    return games

def playerInList(target, players):
    for player in players:
        if target.lower() in player.lower():
            return True
    return False

def addTeamGames(games, team, onlyUpcoming, onlySoon):
    # Fetch games from proper location
    match team['league']:
        case 'KHL':
            games = fetchKHLGames(games, team, onlyUpcoming, onlySoon)
        case _:
            print("ERROR: Could not find leage <" + team['league'] + ">")

    # Sort games before returning to user
    games.sort(key=lambda e: e.gametime)

    return games