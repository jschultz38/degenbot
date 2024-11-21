class HockeyGame:
    """Structure to hold hockey games.

    Attributes:
        team (json): The degen team that is playing in the game.
        gametime (datetime): Time of the game.
        location (string): Name of the rink.
        home_team (string): Name of the home team.
        away_team (string): Name of the away team.
        degen_team (bool): Whether the degen is away or home.
        home_score (int): Score of the home team, if any (default None)
        away_score (int): Score of the away team, if any (default None)
        game_id (str): proprietaty game id from each site (default None)
        score_sheet (str): URL to access game scoresheets
    """

    def __init__(self, team, datetime_obj, location, home_team, away_team, degen_home, home_score=None, away_score=None, season_id = None, game_id=None, score_sheet_url = None):
        # this is the json object of the team - should look the same as in res/team_data.json
        self.team = team
        self.gametime = datetime_obj
        self.location = location
        self.home_team = home_team
        self.away_team = away_team
        # This value should be one of the above macros
        self.degen_home = degen_home
        self.home_score = home_score
        self.away_score = away_score
        self.season_id = season_id
        self.result = None
        self.game_id = game_id
        self.score_sheet_url = score_sheet_url

    def to_string(self):
        side = 'HOME' if self.degen_home else 'AWAY'

        # Display the time zone if games are local to a different zone
        time_zone = ' PST' if self.team['league'] == 'AAHL' else ''
        string_repr = self.gametime.strftime("%A, %B %d, %I:%M %p") + time_zone +\
            ", " + self.location + ", " + side + ", "

        # Add in result if there is one
        if self.home_score is not None:
            result = None
            if self.home_score == self.away_score:
                self.result = 'Tie'
                result = 'T'
            elif (self.degen_home and self.home_score > self.away_score) or (not self.degen_home and self.home_score < self.away_score):
                self.result = 'Victory'
                result = 'W'
            else:
                self.result = 'Defeat'
                result = 'L'

            # Formatting the score line depending on if degen is home or away, putting Degen first.
            if self.degen_home:
                string_repr += result + ", " + \
                    str(self.home_score) + " - " + str(self.away_score) + ", "
            else:
                string_repr += result + ", " + \
                    str(self.away_score) + " - " + str(self.home_score) + ", "

        # Add team names, with ^ marking the degen team
        if self.degen_home:
            string_repr += "^" + self.home_team + " vs " + self.away_team
        else:
            string_repr += "^" + self.away_team + " vs " + self.home_team

        return string_repr

    def __str__(self):
        return self.to_string()
