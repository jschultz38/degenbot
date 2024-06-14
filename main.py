import json
import datetime
from utils.player import Suspension

from bot import createBasicBot
from globals import *
from credentials import prod_token, test_token

def main():
    # Read in teams
    print("reading in json...", end ="")

    json_data = None
    with open("res/teams.json") as teams_file:
        json_data = json.load(teams_file)
    teams = json_data["teams"]

    with open("res/seasons.json") as teams_file:
        json_data = json.load(teams_file)
    seasons = json_data

    print('done')

    # Load seasons cache into memory
    print('loading past suspensions...', end ="")

    suss = []
    with open("res/past_seasons_cache.txt", "r", encoding="utf-8") as f:
        for line in f:
            suss.append(eval(line))
    seasons['khl']['past_seasons_cache'] = suss

    print('done')

    # Set up bot
    bot = createBasicBot([teams, seasons])
    bot.run(test_token if USE_TEST_TOKEN else prod_token)

if __name__ == '__main__':
    main()
