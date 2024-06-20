import discord
from datetime import datetime


def create_default_embed(title=None, color=discord.Color.green()):
    em = discord.Embed(title=title, color=color)
    em.set_footer(text="Made by xDDYx's darkest thoughts.")
    return em

def construct_game_embed(games: object, title: object, color: object = discord.Color.green(), showPlayers: bool = False) -> object:
    newembed = create_default_embed(title=title, color=color)
    try:
        newembed.set_thumbnail(url=games[0].team['logo_url'])
    except Exception:
        newembed.set_thumbnail(url="https://krakenhockeyleague.com/hockey/images/teamlogos100/Degens.png")

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

        if showPlayers:
            title += " - " + ", ".join(game.team['players'])

        newembed.add_field(name=title, value=score, inline=False)


    return newembed
