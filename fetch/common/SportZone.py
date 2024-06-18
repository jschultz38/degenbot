import datetime
from utils.game import HockeyGame
from utils.common import translateMonth

def createSportZoneGame(cols, team):
    # Get the easy stuff
    location = cols[3].getText()
    degen_team = team['name']
    side = cols[4].getText()
    is_degen_home = (side == "HOME")

    # Add result-dependant variables
    cols_text = None
    opponent_team = None
    away_score = None
    home_score = None
    if ("Preview" in cols[-1].getText()):
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

        if is_degen_home:
            home_score = degen_score
            away_score = opponent_score
        else:
            home_score = opponent_score
            away_score = degen_score

    # Place teams on home/away
    if is_degen_home:
        home_team = degen_team
        away_team = opponent_team
    else:
        home_team = opponent_team
        away_team = degen_team

    # Find game time
    dateText = cols[1].getText()
    timeText = cols[2].getText()

    ## Get day
    day_ret = int(dateText.split(" ")[2])

    ## Get month
    month_ret = translateMonth(dateText.split(" ")[1])
        
    ## Get time
    hour = timeText.split(":")[0]
    minute = timeText.split(":")[1].split(" ")[0]
    meridiem = timeText.split(":")[1].split(" ")[1]

    hour_ret = int(hour) if meridiem == "AM" else int(hour) + 12
    minute_ret = int(minute)

    gametime = datetime.datetime(2024, month_ret, day_ret, hour=hour_ret, minute=minute_ret)
    
    # Create the game
    game = HockeyGame(
                team,
                gametime,
                location,
                home_team,
                away_team,
                HockeyGame.DEGEN_HOME if is_degen_home else HockeyGame.DEGEN_AWAY,
                home_score=home_score,
                away_score=away_score
                )

    return game
