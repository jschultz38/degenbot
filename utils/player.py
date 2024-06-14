class Suspension:
    def __init__(self, date, name, team, div, games, sus_id):
        # this is the json object of the team - should look the same as in res/teams.json

        # Note: Due to the fact that serialization uses "" for strings, we need to replace them with ''
        self.date = date
        self.name = str(name).replace('"', "'")
        self.team = str(team).replace('"', "'")
        self.div = str(div).replace('"', "'")
        self.games = str(games).replace('"', "'")
        self.sus_id = str(sus_id).replace('"', "'")

    def to_string(self):
        string_repr = f'{self.name}, {self.games} games, {self.date.strftime("%m/%d/%Y")}, {self.team}, ' \
                    f'{self.div}, [Details](<https://krakenhockeyleague.com/suspension-details/{self.sus_id}>)'

        return string_repr

    def __str__(self):
        return self.to_string()

    def __repr__(self):
        '''This is specifically for serialization. The only catch here is the serialization of date,
        which is a datetime object. I've decided that in suspensions, we only care about {year, month,
        day} so that's exactly how we serialize it.

        Note: eval() disallows zero-padded integers and since %-m does not exist on windows, I had to 
        improvise with the replace(...) method you see below.

        Note 2: The triple quotes are because of course some of the names have quotes in them... ?!?'''
        return f'Suspension({self.date.strftime('datetime.datetime(year=int(%Y), month=int(%m), day=int(%d))').replace('(0', '(')}, "{self.name}",' \
                f' "{self.team}", "{self.div}", "{self.games}", "{self.sus_id}")'
