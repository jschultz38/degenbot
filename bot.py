import discord
from discord.ext import commands
import random

from fetch.retrieve import retrieveAllGames
from globals import RATE_LIMITED

from res.DegenEmbed import *

def createBasicBot(teams):
    intents = discord.Intents.default()
    intents.message_content = True

    bot = commands.Bot(command_prefix='!', intents=intents, help_command=MyHelpCommand())

    @bot.command(
        help = bot.command_prefix + "schedule <name> - Shows all games"
        )
    async def schedule(ctx, player=None):
        if player == None:
            await ctx.send("Please input a player name after your command")
            return

        onlyUpcoming = False
        onlySoon = False

        games = retrieveAllGames(teams, player, onlyUpcoming, onlySoon)
        await sendGames(ctx, games, player, onlySoon)

    @bot.command(
        help = bot.command_prefix + "upcoming <name> - Shows all upcoming games"
        )
    async def upcoming(ctx, player=None):
        if player == None:
            await ctx.send("Please input a player name after your command")
            return
            
        onlyUpcoming = True
        onlySoon = False

        games = retrieveAllGames(teams, player, onlyUpcoming, onlySoon)
        await sendGames(ctx, games, player, onlySoon)

    @bot.command(
        help = bot.command_prefix + "soon <?name?> - Shows all games for the next week"
        )
    async def soon(ctx, player=None):    
        onlyUpcoming = False
        onlySoon = True

        games = retrieveAllGames(teams, player, onlyUpcoming, onlySoon)
        await sendGames(ctx, games, player, onlySoon)

    @bot.command(
        help = bot.command_prefix + "fuck <?name?>"
        )
    async def fuck(ctx, person=''):
        fuckEmbed = DegenEmbed( title=None, description= None, color=discord.Color.red())
        fuckEmbed.create()
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
        await ctx.send("fuck " + people[0] + ", marry " + people[1] + ", kill " + people[2])
 
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

async def sendGames(ctx, games, player, onlySoon):
    print_str = ''
    if RATE_LIMITED:
        print_str += "Note: I've been rate limited :(\n"

    if len(games) == 0:
        print_str += 'No games found'
    else:
        for game in games:
            game_str = game.to_string()
            if onlySoon and player == None:
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
