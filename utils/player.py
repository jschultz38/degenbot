class Suspension:
    def __init__(self, date, name, team, div, games, sus_id):
        # this is the json object of the team - should look the same as in res/teams.json
        self.date = date
        self.name = name
        self.team = team
        self.div = div
        self.games = games
        self.sus_id = sus_id

    def to_string(self):
        string_repr = f'{self.name}, {self.games} games, {self.date.strftime("%m/%d")}, {self.team},' \
                    f'{self.div}, [Web page](https://krakenhockeyleague.com/suspension-details/{self.sus_id})'

        return string_repr

    def __str__(self):
        return self.to_string()
