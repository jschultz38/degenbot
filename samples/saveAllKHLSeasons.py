''' IMPORTANT!!!!

# Running
from top directory in repo, run `python -m samples.saveAllKHLSeasons`

# Updating
If you want to update because a new season has started, you need to refresh
allKHLSeasons.txt. I think I just clicked the season drop-down box on the
KHL suspensions page and then pasted the HTML from inspection in chrome.

'''

from utils.player import Suspension
from fetch.khl import fetchKHLSuspensions

import json
import datetime

season_ids = []
current_seasons = [2118]

#Figure out how to download allKHLSeasons dynamically

# Read in current seasons
with open("samples/allKHLSeasons.txt", "r") as f:
	while line := f.readline():
		if len(line) >= 3 and line[:3] == "<li":
			season_id = line.split("=")[3].split('"')[0]
			season_ids.append(int(season_id))

# Write to json file in proper format
with open("res/seasons.json", "w") as f:
	past_seasons = [s for s in season_ids if s not in current_seasons]
	print(past_seasons)

	dictionary = {
					'khl': 	{
							'current_seasons': current_seasons,
							'past_seasons': past_seasons
							}
				}

	json_obj = json.dumps(dictionary, indent=4)
	f.write(json_obj)

# Prepare previous seasons cache file
khl_seasons = dictionary['khl']
khl_seasons['current_seasons'] = khl_seasons['past_seasons']
suss = fetchKHLSuspensions(khl_seasons)
with open("res/past_seasons_cache.txt", "w", encoding="utf-8") as f:
	for s in suss:
		f.write(repr(s) + "\n")

'''
# You can use this for checking the output
new_suss = []
with open("res/past_seasons_cache.txt", "r") as f:
	for line in f:
		new_suss.append(eval(line))

for n in new_suss:
	print(type(s))
	print(s)

print(suss[0])
print(new_suss[0])
print(str(suss[0]) == str(new_suss[0]))'''




#seasons_dict = dict(zip(season_ids, ['']*len(season_ids)))