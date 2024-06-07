class HockeyGame:
    def __init__(self, team, textual_rep, gametime, gameurl):
        self.team = team
        self.text = textual_rep
        self.gametime = gametime
        self.gameurl = gameurl

    def __str__(self):
        return self.text