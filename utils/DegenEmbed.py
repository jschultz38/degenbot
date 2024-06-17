import discord
from datetime import datetime


class DegenEmbed(discord.Embed):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def create(self, thumbnail=None, title=None):
        if thumbnail:
            self.set_thumbnail(url=thumbnail)
        if title:
            self.title = title
        self.set_footer(text="Made by xDDYx's darkest thoughts.")

    def add_field(self, name, value, inline=False):
        super().add_field(name=name, value=value, inline=inline)

    @staticmethod
    def construct_full_embed(games: object, title: object, color: object) -> object:
        newembed = DegenEmbed(title=title, color=color)
        try:
            newembed.create(games[0].team['logo_url'], title)
        except Exception:
                newembed.create("https://krakenhockeyleague.com/hockey/images/teamlogos100/Degens.png", title)

        for game in games:
            if game.gametime <= datetime.now():
                if game.degen_home:
                    if game.home_score > game.away_score:
                        result = "Victory"
                    elif game.home_score < game.away_score:
                        result = "Defeat"
                    else:
                        result = "Tie"
                    title = f'{game.home_team} {result} Vs. {game.away_team} on {game.gametime.strftime("%B %d")}'
                    score = f'{game.home_team}: {game.home_score} - {game.away_team}: {game.away_score}'
                else:
                    if game.home_score < game.away_score:
                        result = "Victory"
                    elif game.home_score > game.away_score:
                        result = "Defeat"
                    else:
                        result = "Tie"
                    title = f'{game.away_team} {result} @ {game.home_team} on {game.gametime.strftime("%B %d")}'
                    score = f'{game.away_team}: {game.away_score} - {game.home_team}: {game.home_score}'
            else:
                if game.degen_home:
                    title = f'{game.home_team} Vs. {game.away_team}'
                else:
                    title = f'{game.away_team} @ {game.home_team}'
                score = f'{game.gametime.strftime("%B %d %I:%M %p")} @ {game.location}'

            newembed.add_field(name=title, value=score, inline=False)


        return newembed