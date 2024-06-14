from datetime import datetime, timedelta, timezone
import discord
from discord.ext import commands
import random
import requests

from globals import TEST_MODE
from fetch.retrieve import retrieveAllGames, retrieveSuspensions

from utils.DegenEmbed import *

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
        """So there is now way to store extra information in a context like
        there is with a command, so I have to create it myself. If at some
        point in the future this is added, I log this error so that I won't
        be messing something up
        """
        if hasattr(ctx, 'extras'):
            print("ERROR: extras found in Context")
        ctx.extras = {'before_time': datetime.now()}

    @bot.after_invoke
    async def after_command(ctx):
        print("time to respond is: " + str(datetime.now() - ctx.extras['before_time']))

    async def on_error(ctx, error):
        if isinstance(error, commands.UserInputError):
            await ctx.send("I cant understand you when you use ' or \"")
            print("handled error: " + str(error))
            return
        raise error
    bot.on_command_error = on_error

    @bot.command(
        help=bot.command_prefix + "schedule <name> - Shows all games"
        )
    async def schedule(ctx, player=None):
        if player == None:
            await ctx.send("Please input a player name after your command")
            return

        games = retrieveAllGames(teams, player)

        await sendGames(ctx, games, False)

    @bot.command(
        help=bot.command_prefix + "upcoming <name> - Shows all upcoming games"
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
        # will pick the logo for the nearest game. Only works if games are present. We should make sure every team has a logo.
        try:
            upcomingEmbed.create(games[0].team['logo_url'])
        except Exception:
            print('No logo found')
            upcomingEmbed.create("https://krakenhockeyleague.com/hockey/images/teamlogos100/Degens.png")
            pass
        for game in games:
            timediff = time_now - game.gametime
            #if timedelta(seconds=0) < timediff < timedelta(hours=1):
               # upcomingEmbed.add_field(f"{game.away_team} vs {game.home_team}", f"[{game.gametime} @ {game.location} (Watch Live)](https://livebarn.com/en/video/{game.rinkid}/live)")
            #else:
            upcomingEmbed.add_field(f'{game.away_team} vs {game.home_team}', f'{game.gametime} @ {game.location}')

        await ctx.send(embed=upcomingEmbed)

    @bot.command(
        help=bot.command_prefix + "soon <?name?> - Shows all games for the next week"
        )
    async def soon(ctx, player=None):
        games = retrieveAllGames(teams, player)

        # Filter out games
        time_now = datetime.now()
        today = datetime(time_now.year, time_now.month, time_now.day)
        games = [game for game in games if game.gametime >= today and (game.gametime - today) <= timedelta(days=8)]

        await sendGames(ctx, games, (player == None))

    @bot.command(
        help=bot.command_prefix + "next <?name?> - Shows next game for the person requested"
    )
    async def next(ctx, player=None):
        games = retrieveAllGames(teams, player)
        if player:
            nextEmbed = DegenEmbed(title=f"Next Game for {player}", description=None, color=discord.Color.red())
        else:
            nextEmbed = DegenEmbed(title=f"Next Game", description=None, color=discord.Color.red())
        nextEmbed.create("https://avatars.githubusercontent.com/u/1737241?v=4")
        time_now = datetime.now()
        for game in games:
            if game.gametime >= time_now:
                nextEmbed.add_field(f'{game.away_team} vs {game.home_team}', f'{game.gametime} @ {game.location}')
                break
        await ctx.send(embed=nextEmbed)

    @bot.command(
        help=bot.command_prefix + "today <?name?> - Shows all games happening today"
        )
    async def today(ctx, player=None):
        games = retrieveAllGames(teams, player)

        # Filter out games
        time_now = datetime.now()
        today = datetime(time_now.year, time_now.month, time_now.day)
        games = [game for game in games if game.gametime >= today and (game.gametime - today) < timedelta(days=1)]

        await sendGames(ctx, games, player==None)

    @bot.command(
        help=bot.command_prefix + "tomorrow <?name?> - Shows all games happening tomorrow"
        )
    async def tomorrow(ctx, player=None):
        games = retrieveAllGames(teams, None)

        # Filter out games
        time_now = datetime.now()
        today = datetime(time_now.year, time_now.month, time_now.day)
        tomorrow = today + timedelta(days=1)
        games = [game for game in games \
                 if game.gametime >= today and timedelta(days=1) <= (game.gametime - today) < timedelta(days=2)]

        await sendGames(ctx, games, player==None)

    @bot.command(
        help=bot.command_prefix + "sus - Shows all current suspensions"
        )
    async def sus(ctx):
        suss = retrieveSuspensions()
        await ctx.send("\n".join(map(str, suss)))

    @bot.command(
        help=bot.command_prefix + "fuck <?name?>",
        extras= {'meme': True}
        )
    async def fuck(ctx, *things):
        person = ' '.join(things)
        fuckEmbed = DegenEmbed( title=None, description= None, color=discord.Color.red())
        fuckEmbed.create("https://avatars.githubusercontent.com/u/1737241?v=4")
        fuckEmbed.add_field(f'Fuck {person}', f'Get Fucked {person}')
        await ctx.send(embed = fuckEmbed)

    @bot.command(
        help=bot.command_prefix + "updog",
        extras= {'meme': True}
        )
    async def updog(ctx):
        await ctx.send("what's up dog?")

    @bot.command(
        help=bot.command_prefix + "fmk <name> <name> <name>",
        extras= {'meme': True}
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
        help=bot.command_prefix + "stepcaptain",
        extras= {'meme': True}
    )
    async def stepcaptain(ctx):
        await ctx.send('https://imgur.com/VJyQs2L')

    @bot.command(
        help = bot.command_prefix + "chirp <name> - can @ someone or just put a name",
        extras = {'meme': True}
    )
    async def chirp(ctx, user=None):
        if user is None:
            await ctx.send("Give me someone to chirp!")
            return

        base_string = requests.get("https://evilinsult.com/generate_insult.php/")
        chirp = f'{user}, {base_string.text}'

        await ctx.send(chirp)

    @bot.command(
        help=bot.command_prefix + "ruf :|",
        extras= {'meme': True}
    )
    async def ruf(ctx):
        await ctx.send('https://imgur.com/q4OWXNs')

    @bot.command(
        help=bot.command_prefix + "pat - god i miss that man",
        extras= {'meme': True}
    )
    async def pat(ctx):
        if not 'pat' in ctx.command.extras:
            ctx.command.extras['pat'] = random.randint(100,500)

        ctx.command.extras['pat'] += 1

        await ctx.send('Pat has been missed ' + str(ctx.command.extras['pat']) +
                        ' times since this bot was started')

    @bot.command(
        extras={'meme': True}
    )
    async def goon(ctx):
        await ctx.send('https://i.imgflip.com/8teknw.jpg')

    @bot.command(
        help=bot.command_prefix + "no",
        extras= {'meme': True}
    )
    async def no(ctx):
        await ctx.send('https://private-user-images.githubusercontent.com/2738715/338701955-9f01d50d-8d02-465a-bd3c-653f411bcbc6.png?jwt=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3MTgyNTg0MzAsIm5iZiI6MTcxODI1ODEzMCwicGF0aCI6Ii8yNzM4NzE1LzMzODcwMTk1NS05ZjAxZDUwZC04ZDAyLTQ2NWEtYmQzYy02NTNmNDExYmNiYzYucG5nP1gtQW16LUFsZ29yaXRobT1BV1M0LUhNQUMtU0hBMjU2JlgtQW16LUNyZWRlbnRpYWw9QUtJQVZDT0RZTFNBNTNQUUs0WkElMkYyMDI0MDYxMyUyRnVzLWVhc3QtMSUyRnMzJTJGYXdzNF9yZXF1ZXN0JlgtQW16LURhdGU9MjAyNDA2MTNUMDU1NTMwWiZYLUFtei1FeHBpcmVzPTMwMCZYLUFtei1TaWduYXR1cmU9ODQ3NGMzMDlkMmNiOTBlOWQyY2FjNWUwMTZiNGQzZTVkMGU5ODlmZjhjZWYxMzIzNTYxNWVhNDNlMDQwMjdlOSZYLUFtei1TaWduZWRIZWFkZXJzPWhvc3QmYWN0b3JfaWQ9MCZrZXlfaWQ9MCZyZXBvX2lkPTAifQ.cgV09ggpWbI_HMqqRHLVwmzc7LmDlI9ZuIg1D9gQ0RQ')

    return bot

async def sendGames(ctx, games, showPlayers):
    print_str = ''
    if TEST_MODE:
        print_str += "Note: Testing mode\n"

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
        preamble = "<> means required, <??> means optional"
        print_str_real = ''
        print_str_meme = ''
        print_str_help = ''
        for cog, cmds in mappings.items():
            cmds = await self.filter_commands(cmds, sort=True)
            for cmd in cmds:
                if not cmd.help:
                    continue

                if cmd.name == 'help':
                    print_str_help += '!help - ' + cmd.help + "\n"
                elif 'meme' in cmd.extras and cmd.extras['meme']:
                    print_str_meme += cmd.help + "\n"
                else:
                    print_str_real += cmd.help + "\n"

        await self.context.send(preamble + "\n\n" + print_str_real + print_str_help + "\n" + print_str_meme)
