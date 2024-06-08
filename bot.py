from datetime import datetime, timedelta, timezone
import discord
from discord.ext import commands
import random

from fetch.retrieve import retrieveAllGames
from globals import RATE_LIMITED

from res.DegenEmbed import *

def createBasicBot(teams):
    intents = discord.Intents.default()
    intents.message_content = True

    bot = commands.Bot(
        command_prefix='!',
        intents=intents,
        help_command=MyHelpCommand(),
        case_insensitive=True
        )

    @bot.before_invoke
    async def before_command(ctx):
        ctx.before_time = datetime.now()

    @bot.after_invoke
    async def after_command(ctx):
        time_created = ctx.before_time
        now = datetime.now()
        print("time to respond is: " + str(now - time_created))

    @bot.command(
        help = bot.command_prefix + "schedule <name> - Shows all games"
        )
    async def schedule(ctx, player=None):
        if player == None:
            await ctx.send("Please input a player name after your command")
            return

        games = retrieveAllGames(teams, player)
        await sendGames(ctx, games, False)

    @bot.command(
        help = bot.command_prefix + "upcoming <name> - Shows all upcoming games"
        )
    async def upcoming(ctx, player=None):
        if player == None:
            await ctx.send("Please input a player name after your command")
            return

        games = retrieveAllGames(teams, player)
  
        # Filter out games
        time_now = datetime.now()
        today = datetime(time_now.year, time_now.month, time_now.day)
        games = [game for game in games if game.gametime >= today]

        upcomingEmbed = DegenEmbed(title=f"Upcoming Games for {player}", description=None, color=discord.Color.red())
        upcomingEmbed.create("https://avatars.githubusercontent.com/u/1737241?v=4")
        for game in games:
            timediff = time_now - game.gametime
            #if timedelta(seconds=0) < timediff < timedelta(hours=1):
               # upcomingEmbed.add_field(f"{game.away_team} vs {game.home_team}", f"[{game.gametime} @ {game.location} (Watch Live)](https://livebarn.com/en/video/{game.rinkid}/live)")
            #else:
            upcomingEmbed.add_field(f'{game.away_team} vs {game.home_team}', f'{game.gametime} @ {game.location}')

        await ctx.send(embed=upcomingEmbed)

    @bot.command(
        help = bot.command_prefix + "soon <?name?> - Shows all games for the next week"
        )
    async def soon(ctx, player=None):
        games = retrieveAllGames(teams, player)

        # Filter out games
        time_now = datetime.now()
        today = datetime(time_now.year, time_now.month, time_now.day)
        for game in games:
            if not (game.gametime > today and (game.gametime - today) < timedelta(days=7)):
                games.remove(game)
        games = [game for game in games if game.gametime >= today and (game.gametime - today) < timedelta(days=7)]

        await sendGames(ctx, games, (player == None))

    @bot.command(
        help = bot.command_prefix + "fuck <?name?>"
        )

    async def fuck(ctx, *things):
        person = ' '.join(things)
        fuckEmbed = DegenEmbed( title=None, description= None, color=discord.Color.red())
        fuckEmbed.create("https://avatars.githubusercontent.com/u/1737241?v=4")
        fuckEmbed.add_field(f'Fuck {person}', f'Get Fucked {person}')
        await ctx.send(embed = fuckEmbed)

    @bot.command(
        help = bot.command_prefix + "updog"
        )
    async def updog(ctx):
        await ctx.send("what's up dog?")

    @bot.command(
        help = bot.command_prefix + "fmk <name> <name> <name>"
        )
    async def fmk(ctx, person1=None, person2=None, person3=None):
        if person1 == None or person2 == None or person3 == None:
            await ctx.send("please send 3 names")
            return
        people = [person1, person2, person3]
        random.shuffle(people)
        fmkEmbed = DegenEmbed(title=None, description=None, color=discord.Color.pink())
        fmkEmbed.create("https://pngimg.com/d/kim_jong_un_PNG37.png")
        fmkEmbed.add_field(f"Fuck {people[0]} \U0001F346", f"Get Fucked, {people[0]} ")
        fmkEmbed.add_field(f"Marry {people[1]} \U0001F48D", f"How sweet, {people[1]}")
        fmkEmbed.add_field(f"Kill {people[2]} \U0001F52A", f"I guess you'll just die, {people[2]}")

        await ctx.send(embed = fmkEmbed)
 
    @bot.command(
        help = bot.command_prefix + "stepcaptain"
    )
    async def stepcaptain(ctx):
        await ctx.send('https://imgur.com/VJyQs2L')

    @bot.command(
        help=bot.command_prefix + "ruf :|"
    )
    async def ruf(ctx):
        await ctx.send('https://imgur.com/q4OWXNs')
    
    return bot

async def sendGames(ctx, games, showPlayers):
    games.sort(key=lambda e: e.gametime)

    print_str = ''
    if RATE_LIMITED:
        print_str += "Note: I've been rate limited :(\n"

    if len(games) == 0:
        print_str += 'No games found'
    else:
        for game in games:
            game_str = game.to_string()
            if showPlayers:
                game_str += ' - ' + ', '.join(game.team['players'])

            # Discord has a requirement that all messages are less than 2000 characters
            if len(print_str) + 1 + len(game_str) > 2000:
                await ctx.send(print_str)
                print_str = ''

            if len(print_str) > 0:
                print_str += '\n'
            print_str += game_str

    await ctx.send(print_str)

class MyHelpCommand(commands.HelpCommand):
    async def send_bot_help(self, mappings):
        print_str = "<> means required, <??> means optional\n\n"
        for cog, cmds in mappings.items():
            cmds = await self.filter_commands(cmds, sort=True)
            for cmd in cmds:
                if cmd.name == 'help':
                    print_str += '!help - ' + cmd.help + "\n"
                else:
                    print_str += cmd.help + "\n"
        await self.context.send(print_str)
