import datetime
from utils.common import translateMonth
from utils.hockey_game import HockeyGame

'''Sportzone is a backend that apparently multiple organization use.
This file should work for any website that uses sportszone on the
webpage
'''


def createSportZoneGame(cols, team, heading=None):
    # Get the easy stuff - using the teams schedule page
    location = cols[3].getText()

    #Get the game ID for the game and use it to build the scoresheet URL if game ID exists
    game_id=None
    score_sheet_url = None
    try:
        game_id = cols[8].contents[0].attrs['href'].split('/')[2]
        score_sheet_url = f"https://krakenhockeyleague.com/scoresheet-complete/{game_id}"
    except IndexError:
        print("Warning: Could not get game ID; cannot build score sheet")
        pass

    degen_team = team['name']
    side = cols[4].getText()
    DEGEN_HOME = True if side == 'HOME' else False

    # Add result-dependant variables
    cols_text = None
    opponent_team = None
    away_score = None
    home_score = None
    if ("Final" not in cols[-1].getText()):
        opponent_team = cols[-4].getText()
    else:
        opponent_team = cols[5].getText()
        score_text = cols[7].getText().split(" ")
        result = cols[6].span.getText().strip()
        if result == 'W':
            degen_score = int(score_text[0])
            opponent_score = int(score_text[2])
        else:
            degen_score = int(score_text[2])
            opponent_score = int(score_text[0])

        if DEGEN_HOME:
            home_score = degen_score
            away_score = opponent_score
        else:
            home_score = opponent_score
            away_score = degen_score

    # Place teams on home/away
    if DEGEN_HOME:
        home_team = degen_team
        away_team = opponent_team
    else:
        home_team = opponent_team
        away_team = degen_team

    # Find game time & date
    dateText = cols[1].getText()
    timeText = cols[2].getText()

    ## Get date
    day_ret = int(dateText.split(" ")[2])
    month_ret = translateMonth(dateText.split(" ")[1])
    #Using the heading from the schedule to figure out the year.
    year = int(heading.getText().split(" ")[1]) if heading else 2024

    ## Get time
    hour = timeText.split(":")[0]
    minute = timeText.split(":")[1].split(" ")[0]
    meridiem = timeText.split(":")[1].split(" ")[1]

    hour_ret = int(hour) if meridiem == "AM" else int(hour) + 12
    minute_ret = int(minute)

    gametime = datetime.datetime(
        year, month_ret, day_ret, hour=hour_ret, minute=minute_ret)

    # Create the game
    game = HockeyGame(
        team,
        gametime,
        location,
        home_team,
        away_team,
        DEGEN_HOME,
        home_score=home_score,
        away_score=away_score,
        game_id=game_id,
        score_sheet_url=score_sheet_url
    )

    return game
