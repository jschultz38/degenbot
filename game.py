# previous
# Tue, May 14, 9:20 PM, KCI VMFH, AWAY, W, 9 - 1, ^BSOD vs Monarchs 5D
#
# upcoming
# Thu, Jun 13, 8:00 PM, KVIC, HOME, ^BSOD vs Highlanders

# What do I need?
# - datetime of the game, rink, teams, side of teams, side of degen
# + (for completed games) score with side of team

# - datetime of the game
# - rink
# - home team
# - away team
# - degen team
###############
# - home score
# - away score

class HockeyGame:
    # Macros used for dictating which team the degen is on
    DEGEN_HOME = 0
    DEGEN_AWAY = 1

    def __init__(self, team, datetime_obj, location, home_team, away_team, degen_team, home_score=None, away_score=None):
        # this is the json object of the team - should look the same as in res/teams.json
        self.team = team
        self.gametime = datetime_obj
        self.location = location
        self.home_team = home_team
        self.away_team = away_team
        # This value should be one of the above macros
        self.degen_team = degen_team
        self.home_score = home_score
        self.away_score = away_score

    def to_string(self):
        is_degen_home = (self.degen_team == self.DEGEN_HOME)
        side = 'HOME' if is_degen_home else 'AWAY'

        string_repr = self.gametime.strftime("%A, %B %d, %I:%M %p") + ", " + \
                        self.location + ", " + \
                        side + ", "

        # Add in result if there is one
        if self.home_score != None:
            result = None
            if self.home_score == self.away_score:
                result = 'T'
            elif (is_degen_home and self.home_score > self.away_score) or (not is_degen_home and self.home_score < self.away_score):
                result = 'W'
            else:
                result = 'L'

            if is_degen_home:
                string_repr += result + ", " + \
                                str(self.home_score) + " - " + str(self.away_score) + ", "
            else:
                string_repr += result + ", " + \
                                str(self.away_score) + " - " + str(self.home_score) + ", "

        # Add team names, with ^ marking the degen team
        if is_degen_home:
            string_repr += "^" + self.home_team + " vs " + self.away_team
        else:
            string_repr += "^" + self.away_team + " vs " + self.home_team

        return string_repr

    def __str__(self):
        return self.to_string()
