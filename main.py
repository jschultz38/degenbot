import json
import datetime
import threading

from bot import createBasicBot
from globals import *
from credentials import prod_token, test_token
from utils.player import Suspension
from utils.common import findAllKHLSeasons
from cache.cache import main_caching_loop


def main():
    # Read in team data
    print("reading in json...", end="")

    team_data = None
    with open("res/team_data.json") as teams_file:
        team_data = json.load(teams_file)

    print('done')

    # Handle suspensions
    if ENABLE_SUSPENSIONS:
        print('loading past suspensions...', end="")

        # Init all seasons
        all_seasons = findAllKHLSeasons()
        team_data['suspensions'] = {
            'khl': {}
        }
        for season in all_seasons:
            team_data['suspensions']['khl'][season] = {}

        print('done')
    else:
        print('suspensions disabled')

    # Handle caching
    cache_thread = None
    restart_caching_event = None
    if ENABLE_CACHING:
        print("caching enabled, spinning up the thread...")

        restart_caching_event = threading.Event()
        cache_thread = threading.Thread(target=main_caching_loop, args=(
            team_data, restart_caching_event), daemon=True)
        cache_thread.start()
    else:
        print("caching disabled")

    # Set up bot
    print("starting bot thread...")
    extras = {
        'suspensions_enabled': ENABLE_SUSPENSIONS
    }
    bot = createBasicBot(team_data, restart_caching_event, extras)
    bot.run(test_token if USE_TEST_TOKEN else prod_token)


if __name__ == '__main__':
    main()
