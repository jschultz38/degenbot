import random
from time import sleep

from fetch.retrieve import addTeamGames
from globals import CACHING_LOCK

seconds_between_updates = 5 * 60

''' Caching

There are three stages to the caching thread. They simply go in
a rotating order (1->2->3->1->etc.). The stages are:

1. populate the cache - populate each team's cache if it hasn't been populated already
2. update the cache - update a cache entry once every ~seconds_between_updates~ in perpetuity
3. refresh the cache - if we receive ~restart_caching_event~, refresh all entries in the cache
'''

def main_caching_loop(teams, restart_caching_event):
	# Delay a bit so that the bot gets started up properly
	sleep(5)

	while True:
		'''Populate all cache entries that haven't been populated yet'''
		populate_cache(teams)

		'''Refresh cache entries every ~seconds_between_updates~'''
		cache_update_loop(teams, restart_caching_event)

		'''When we receive ~restart_caching_event~, the loop returns
		and this method invalidates all cache entries'''
		invalidate_cache(teams)

def populate_cache(teams):
	print("populating the game cache...")

	for team in teams:
		update_entry_if_needed(team)

	print("game cache fully populated")

def cache_update_loop(teams, restart_caching_event):
	next_index_to_update = 0

	while True:
		sleep(seconds_between_updates)

		if restart_caching_event.is_set():
			restart_caching_event.clear()
			return

		team_to_update = teams[next_index_to_update]

		invalidate_cache_entry(team_to_update)
		update_entry_if_needed(team_to_update)

		next_index_to_update = (next_index_to_update + 1) % len(teams)

def invalidate_cache(teams):
	print("invalidating the game cache...")

	for team in teams:
		invalidate_cache_entry(team)

	print("game cache fully invalidated")

def update_entry_if_needed(team):
	CACHING_LOCK.acquire()

	if 'cache' not in team:
		print("START_UPDATE " + team['name'])

		addTeamGames([], team)

		print("FINISH_UPDATE " + team['name'])
	else:
		print("NO_UPDATE: " + team['name'])

	CACHING_LOCK.release()

def invalidate_cache_entry(team):
	CACHING_LOCK.acquire()
	print("INVALIDATE " + team['name'])
	if 'cache' in team:
		del team['cache']
	CACHING_LOCK.release()
	
