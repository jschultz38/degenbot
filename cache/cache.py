import random
from time import sleep

from fetch.retrieve import addTeamGames
from globals import CACHING_LOCK

seconds_between_updates = 5 * 60

def main_caching(lock, teams):
	# Delay a bit so that the bot gets started up properly
	sleep(5)

	# Populate the cache
	print("populating the cache...")
	for team in teams:
		if 'cache' not in team:
			update_team(team)
			sleep(1)

	print("cache fully populated")

	# Update entries over time
	while True:
		non_updated_entries = list(range(len(teams)))

		while non_updated_entries:
			sleep(seconds_between_updates)

			non_updated_entries_index_to_update = random.randrange(len(non_updated_entries))
			teams_index_to_update = non_updated_entries[non_updated_entries_index_to_update]
			entry_to_update = teams[teams_index_to_update]

			update_team(teams[teams_index_to_update])

			del non_updated_entries[non_updated_entries_index_to_update]

def update_team(team):
	CACHING_LOCK.acquire()

	print("updating team cache " + team['name'])
	print("START")
	if 'cache' in team:
		del team['cache']
	addTeamGames([], team)
	print("FINISH")
	
	CACHING_LOCK.release()
	
