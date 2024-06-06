class HockeyGame:
    def __init__(self, team, textual_rep, gametime):
        self.team = team
        self.text = textual_rep
        self.gametime = gametime

    def __str__(self):
        return self.text
