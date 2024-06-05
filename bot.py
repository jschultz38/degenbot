import discord
from discord.ext import commands
from fetch.retrieve import retrieveAllGames
from globals import RATE_LIMITED

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
        games_str = stringifyGames(games, player, onlySoon)
        await ctx.send(games_str)

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
        games_str = stringifyGames(games, player, onlySoon)
        await ctx.send(games_str)

    @bot.command(
        help = bot.command_prefix + "soon <?name?> - Shows all games for the next week"
        )
    async def soon(ctx, player=None):    
        onlyUpcoming = False
        onlySoon = True

        games = retrieveAllGames(teams, player, onlyUpcoming, onlySoon)
        games_str = stringifyGames(games, player, onlySoon)
        await ctx.send(games_str)

    @bot.command(
        help = bot.command_prefix + "fuck <?name?>"
        )
    async def fuck(ctx, person):
        await ctx.send("fuck " + person)

    @bot.command(
        help = bot.command_prefix + "updog"
        )
    async def updog(ctx):
        await ctx.send("what's up dog?")

    return bot

def stringifyGames(games, player, onlySoon):
    # Return games to user
    ret_str = ''
    if RATE_LIMITED:
        ret_str += "Note: I've been rate limited :(\n"

    if len(games) == 0:
        ret_str += 'No games found'
    else:
        def mapGames(element):
            if onlySoon and player == None:
                return element.text + ' - ' + ', '.join(element.team['players'])
            else:
                return element.text
        games_str = '\n'.join(map(mapGames, games))
        ret_str += games_str

    return ret_str

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