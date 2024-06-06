import datetime
from game import HockeyGame


# Create game object for sportzone backed websites (KHL, Pride)
def createSportZoneGame(cols, team):
    # Create textual representation
    cols_text = None
    if ("Preview" in cols[-1].getText()):
        opponent = cols[-4].getText()
        cols_text = ", ".join(map(lambda e: e.getText(), cols[1:-4:]))
        cols_text += ", ^" + team['name'] + " vs " + opponent
    else:
        opponent = cols.pop(5).getText()
        cols_text = ", ".join(map(lambda e: e.getText(), cols[1:-1:]))
        cols_text += ", ^" + team['name'] + " vs " + opponent
    textual_rep = cols_text

    # Find game time
    dateText = cols[1].getText()
    timeText = cols[2].getText()

    ## Get day
    day_ret = int(dateText.split(" ")[2])

    ## Get month
    month_text = dateText.split(" ")[1]
    month_ret = None

    match month_text:
        case 'Apr':
            month_ret = 4
        case 'May':
            month_ret = 5
        case 'Jun':
            month_ret = 6
        case 'Jul':
            month_ret = 7
        case 'Aug':
            month_ret = 8
        case 'Sep':
            month_ret = 9
        case _:
            print("ERROR: Could not decode: " + month_text)
            month_ret = 1
    month_ret = int(month_ret)

    ## Get time
    hour = timeText.split(":")[0]
    minute = timeText.split(":")[1].split(" ")[0]
    meridiem = timeText.split(":")[1].split(" ")[1]

    hour_ret = int(hour) if meridiem == "AM" else int(hour) + 12
    minute_ret = int(minute)

    gametime = datetime.datetime(2024, int(month_ret), int(day_ret), hour=hour_ret, minute=minute_ret)

    game = HockeyGame(team, textual_rep, gametime)
    print(game)

    return game
