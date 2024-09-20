import json
import datetime
import threading

from bot import createBasicBot
from globals import *
from credentials import prod_token, test_token
from utils.player import Suspension
from cache.cache import main_caching_loop

def main():
    # Read in teams
    print("reading in json...", end ="")

    json_data = None
    with open("res/teams.json") as teams_file:
        json_data = json.load(teams_file)
    teams = json_data["teams"]

    with open("res/seasons.json") as teams_file:
        json_data = json.load(teams_file)
    SEASONS.append(json_data)

    print('done')

    # Load seasons cache into memory
    if ENABLE_SUSPENSIONS:
        print('loading past suspensions...', end ="")

        suss = []
        with open("res/past_seasons_cache.txt", "r", encoding="utf-8") as f:
            for line in f:
                suss.append(eval(line))
        SEASONS[0]['khl']['past_seasons_cache'] = suss

        print('done')
    else:
        print('suspensions disabled')

    # Start caching
    cache_thread = None
    restart_caching_event = None
    if USE_CACHING:
        print("Caching enabled, spinning up the thread...")

        restart_caching_event = threading.Event()
        cache_thread = threading.Thread(target=main_caching_loop, args=(teams, restart_caching_event), daemon=True)
        cache_thread.start()

    # Set up bot
    print("starting bot thread...")
    bot = createBasicBot(teams, restart_caching_event)
    bot.run(test_token if USE_TEST_TOKEN else prod_token)

if __name__ == '__main__':
    main()
