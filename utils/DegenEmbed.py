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

    def construct_full_embed(cls, games: object, title: object, color: object) -> object:
        newembed = DegenEmbed(title=title, color=color)
        try:
            newembed.create(games[0].team['logo_url'], title)
        except Exception:
            newembed.create("https://krakenhockeyleague.com/hockey/images/teamlogos100/Degens.png", title)

        for game in games:
            if game.gametime <= datetime.now():
                newembed.add_field(f'{game.away_team}: {game.away_score} '
                                   f'{game.home_team}: {game.home_score}',
                                   f'{game.gametime.strftime('%B %d')}',
                                   inline=False)
            else:
                newembed.add_field(f'{game.away_team} Vs. {game.home_team} ',
                                   f'{game.gametime} @ {game.location}', inline=False)
        return newembed

