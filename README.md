# Description
Fetch game times for select degenz

# Commands
!help

# Setup

To install required modules: 
```
pip install -r requirements.txt
```
It's good practice to avoid uploading credentials to github, so I've included
them in a file called credentials.py and added it to the gitignore. If you
would like to get this running on your machine, create a file that looks like
this:

```
prod_token = 'prod_token_here'
test_token = 'test_token_here'
```

# TODO
1. Reorganize imports
2. KHL URL defaults to latest season, remove it from everything
3. Figure out if there is a scraper friendly version of KHL: https://github.com/snoking-to-benchapp-csv/snoking-to-benchapp-csv.github.io/wiki

# Features to add
1. Add support for other websites
	- pride tourney
	- pride league
2. Improve cache
	- Add periodic cache invalidation with fuzzy number
	- Make it persistent
5. Add a way to retrieve the livebarn feed
6. Add a filter to commands for things such as location
7. Use https://krakenhockeyleague.com/schedule to figure out KHL seasons dynamically