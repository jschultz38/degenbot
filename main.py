import json
from bot import createBasicBot
from globals import *
from credentials import prod_token, test_token

def main():
    # Read in teams
    json_data = None
    with open("res/teams.json") as teams_file:
        json_data = json.load(teams_file)

    TEAMS = json_data["teams"]

    # Set up bot
    bot = createBasicBot(TEAMS)
    bot.run(test_token if TEST_MODE else prod_token)

if __name__ == '__main__':
    main()