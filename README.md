## What is this
This is a discord bot to scrape games from hockey league websites in the PNW.

## Clone
Clone the repo
`I hope you can figure this out`

## Create a virtual environment
`python -m venv .venv`

## Install modules
`pip install -r requirements.txt`

## Create bots
1. Go to https://discord.com/developers/applications and create a 'New Application'.
2. After including the basic information, head to the 'Bot' tab and enable the
'MESSAGE CONTENT INTENT'. 
3. Still in 'Bot', hit the big button labeled 'Reset Token' and take note of the token
4. If you are planning to use both a prod and test bot, follow the above steps again.
If you don't really know what I'm talking about, it should be good enough to make a
single bot.

## Create credentials.py
It's good practice to avoid uploading credentials to github, so I've included
them in a file called credentials.py and added it to .gitignore. If you
would like to get this running on your machine, create a file that looks like
this with the token from step 3 above:

```
prod_token = 'prod_token_here'
test_token = 'prod_token_here'
open_ai_key = 'open_ai_key_here'
mongo_password = 'mongo_password_here'
admin = ["discord_name1", "discord_name2"]
```

- For the prod_token, paste the token that you took note of in step 3 above
- If you created a test_bot, paste the token from that that bot
- For the open_ai_key and mongo_password, message Fountai2
- For admin, write the discord names that should be given admin access to 
  exectute !cmd commands. Should be your discord name, not server name.

## Add the bot to your test server
1. Return to https://discord.com/developers/applications and open your app
2. Go to the 'OAuth2' tab
3. Under 'OAuth2 URL Generator' enable the 'bot' scope
4. Clicking bot should open up a new field box labeled 'Bot Permissions'. In that,
enable 'Read Messages/View Channels' and 'Send Messages'
5. Copy the generated URL, paste it into a browser, and then invite it to your server of
choice

## Start 'er up
```
source .venv/bin/activate
python main.py
```

On startup, your bot should come online on your discord server and you should see some
prints similar to:
```
2024-06-13 10:27:03 INFO     discord.client logging in using static token
2024-06-13 10:27:04 INFO     discord.gateway Shard ID None has connected to Gateway (Session ID: d7687f87s6d876876df87).
```

## Try it out
`!help`

# Commands
[See commands](https://github.com/jschultz38/degenbot/blob/master/bot.py)

# Testing
Currently, this bot makes quite a few requests to websites with a big list of teams, so sometimes it gets rate limited.
In order to make testing smoother, there is a TEST_MODE which doesn't make any requests to websites and instead reads
from a sample KHL HTML txt in samples/. To use this, set `TEST_MODE=True` in globals.py and test with 
`!schedule jarrett` (or your favorite command).

# Questions
If you have any questions, feel free to message jschultz38
