from datetime import datetime, timedelta, timezone
import discord
from discord.ext import commands
import random
import credentials
from fetch.khl import parse_score_sheet
import requests

from globals import TEST_MODE, ENABLE_SUSPENSIONS, ENABLE_REMOTE_STORAGE, USE_TEST_TOKEN
from fetch.retrieve import retrieveAllGames, retrieveSuspensions
import utils.chatgpt

from utils.degen_embed import *


def createBasicBot(team_data, restart_caching_event, extras):
    intents = discord.Intents.default()
    intents.message_content = True

    bot = commands.Bot(
        command_prefix='!',
        intents=intents,
        help_command=MyHelpCommand(),
        case_insensitive=True
    )

    # Include team data as context
    if hasattr(bot, 'extras'):
        print("ERROR: bot has extras")
    bot.extras = {
        'team_data': team_data,
        'extras': extras
    }

    @bot.before_invoke
    async def before_command(ctx):
        """So there is no way to store extra information in a context like
        there is with a command, so I have to create it myself. If at some
        point in the future this is added, I log this error so that I won't
        be messing something up
        """
        if hasattr(ctx, 'extras'):
            print("ERROR: extras found in Context")
        ctx.extras = {'before_time': datetime.now()}

    @bot.after_invoke
    async def after_command(ctx):
        try:
            if ENABLE_REMOTE_STORAGE and not USE_TEST_TOKEN:
                extras['remote_storage_connection'].write_command(ctx.command.name)
        except Exception as e:
            print(f"Failed to write to mongodb, error:{e}")

        print("time to respond is: " +
              str(datetime.now() - ctx.extras['before_time']))

    async def on_error(ctx, error):
        handled = False

        if isinstance(error, commands.UserInputError):
            await ctx.send("I cant understand you when you use ' or \"")
            handled = True
        if isinstance(error, commands.CommandNotFound):
            await ctx.send("Command not found")
            handled = True

        if handled:
            print("handled error: " + str(error))
            return

        raise error
    bot.on_command_error = on_error

    @bot.command(
        help=bot.command_prefix + "schedule <name> - Shows all games"
    )
    async def schedule(ctx, *args):
        player = " ".join(args)
        if len(player) == 0:
            await ctx.send("Please input a player name after your command")
            return

        games = retrieveAllGames(ctx.bot.extras['team_data'], player)
        embed = construct_game_embed(games, title=f"{player}'s schedule")
        if embed:
            await ctx.send(embed=embed)
        else:
            await sendGames(ctx, games, showPlayers=False)

    @bot.command(
        help = bot.command_prefix + "show result of last game"
                 )
    async def lastgame(ctx, *args):
        player = " ".join(args)
        most_recent = True
        if len(player) == 0:
            await ctx.send("Please input a player name after your command")
            return

        games = retrieveAllGames(ctx.bot.extras['team_data'], player)
        today = datetime(datetime.now().year, datetime.now().month, datetime.now().day)
        games = [game for game in games if game.gametime <= today]
        last_game = None  # Initialize to None
        for game in reversed(games):  # Iterate through games in reverse order
            if game.result is not None:
                last_game = game
                break  # Exit the loop once we find a game with a result
            else:
                most_recent = False

        parse_score_sheet(last_game)
        degen_team = (
            last_game.away_team
            if last_game.away_team == last_game.team['name']
            else last_game.home_team
        )
        degen_score, opp_score = (
            (last_game.away_score, last_game.home_score)
            if degen_team ==last_game.away_team
            else (last_game.home_score, last_game.away_score)
        )
        #I need to figure out why the game result returns none without this print statement.
        print(last_game)
        last_game_message = \
            f"[{last_game.team['name']} {last_game.result} {degen_score} - {opp_score}]({last_game.score_sheet})" \
            if last_game.score_sheet \
            else f"{last_game.team['name']} {last_game.result} {degen_score} - {opp_score}"
        if not most_recent:
            last_game_message = f"Most recent game score has not been updated, here's the last game with a score: \n {last_game_message}"

        await ctx.send(last_game_message)


    @bot.command(
        help=bot.command_prefix + "upcoming <name> - Shows all upcoming games"
    )
    async def upcoming(ctx, *args):
        player = " ".join(args)
        if len(player) == 0:
            await ctx.send("Please input a player name after your command")
            return

        games = retrieveAllGames(ctx.bot.extras['team_data'], player)
        # Filter out games
        time_now = datetime.now()
        today = datetime(time_now.year, time_now.month, time_now.day)
        games = [game for game in games if game.gametime >= today]

        embed = construct_game_embed(
            games, title=f"Upcoming Games for {player}")
        if embed:
            await ctx.send(embed=embed)
        else:
            await sendGames(ctx, games, showPlayers=False)

    @bot.command(
        help=bot.command_prefix + "soon <?name?> - Shows all games for the next week"
    )
    async def soon(ctx, *args):
        player = " ".join(args)
        games = retrieveAllGames(ctx.bot.extras['team_data'], player)

        # Filter out games
        time_now = datetime.now()
        today = datetime(time_now.year, time_now.month, time_now.day)
        games = [game for game in games if game.gametime >=
                 today and (game.gametime - today) <= timedelta(days=8)]
        embed = construct_game_embed(
            games, title=f"Upcoming Games for {player}" if player else "Upcoming Games")
        if embed:
            await ctx.send(embed=embed)
        else:
            await sendGames(ctx, games, (player is None))

    @bot.command(
        help=bot.command_prefix + "next <?name?> - Shows next game for the person requested"
    )
    async def next(ctx, *args):
        player = " ".join(args)
        games = retrieveAllGames(ctx.bot.extras['team_data'], player)
        time_now = datetime.now()
        for game in games:
            if game.gametime >= time_now:
                next_game = [game]
                if player:
                    embed = construct_game_embed(
                        next_game, title=f"Next Game for {player}")
                else:
                    embed = construct_game_embed(
                        next_game, title=f"Next Game with {', '.join(game.team['players'])}")
                break
        if embed:
            await ctx.send(embed=embed)
        else:
            await sendGames(ctx, games, (player is None))

    @bot.command(
        help=bot.command_prefix + "today <?name?> - Shows all games happening today"
    )
    async def today(ctx, *args):
        player = " ".join(args)
        games = retrieveAllGames(ctx.bot.extras['team_data'], player)

        # Filter out games
        time_now = datetime.now()
        today = datetime(time_now.year, time_now.month, time_now.day)
        games = [game for game in games if game.gametime >=
                 today and (game.gametime - today) < timedelta(days=1)]

        if player is None:
            title = f"Games today"
        else:
            title = f"Today's Games for {player}"
        embed = construct_game_embed(
            games, title=title, showPlayers=player is None)
        if embed:
            await ctx.send(embed=embed)
        else:
            await sendGames(ctx, games, (player is None))

    @bot.command(
        help=bot.command_prefix + "tomorrow <?name?> - Shows all games happening tomorrow"
    )
    async def tomorrow(ctx, *args):
        player = " ".join(args)
        games = retrieveAllGames(ctx.bot.extras['team_data'], player)

        # Filter out games
        time_now = datetime.now()
        today = datetime(time_now.year, time_now.month, time_now.day)
        tomorrow = today + timedelta(days=1)
        games = [game for game in games
                 if game.gametime >= today and timedelta(days=1) <= (game.gametime - today) < timedelta(days=2)]

        await sendGames(ctx, games, player is None)

    @bot.command(
        help=bot.command_prefix + "pond <?name?> - Shows all upcoming pond games"
    )
    async def pond(ctx):
        await upcoming(ctx, player="pond")

    @bot.command(
        help=bot.command_prefix + "sus <name> - Shows all current suspensions"
    )
    async def sus(ctx, *args):
        if not ctx.bot.extras['extras']['suspensions_enabled']:
            await ctx.send("!sus is currently disabled, send my creator a message to enable")
            return

        player_name = ' '.join(args)
        if not player_name or len(player_name) < 3:
            await ctx.send("Please input a name with at least 3 characters")
            return

        first_khl_season = ctx.bot.extras['team_data']['suspensions']['khl'][list(
            ctx.bot.extras['team_data']['suspensions']['khl'].keys())[0]]
        if 'cache' not in first_khl_season:
            await ctx.send("First time calling? This might take a while...")

        suss = retrieveSuspensions(ctx.bot.extras['team_data'], player_name)
        if len(suss) > 0:
            message = "\n".join(map(str, suss))
            place = 2000
            while place < len(message):
                await ctx.send(message[place - 2000:place])
                place += 2000
            await ctx.send(message[place - 2000:place])
        else:
            await ctx.send('No suspensions found for ' + player_name)

    @bot.command(
        help = bot.command_prefix + "tldr <yesterday, today, or X hours> - Summarizes what you missed in a thread"
)
    async def tldr(ctx, *, time_frame: str = "today"):
        """

        Args:
            ctx: bot client
            time_frame: a string provided by the user either in a number of hours; "5 hours" or "yesterday" or "today"

        Sends a request to chatgpt to summarize all messages found within a certain timeframe

        Returns: A summary object from chatGPT that it will send in a thread.

        """
        channel = ctx.channel
        now = datetime.now()

        if time_frame.lower() == 'today':
            start_time = now.replace(hour=0, minute=0, second=0, microsecond=0)
        elif time_frame.lower() == "yesterday":
            start_time = (now - timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
        elif "hour" in time_frame.lower():
            try:
                num_hours = int(time_frame.split()[0])
                start_time=now - timedelta(hours=num_hours)
            except ValueError:
                await ctx.send("Invalid time frame. Please specify a valid number of hours (e.g., '5 hours').")
                return
        else:
            await ctx.send("Invalid time frame. Use 'today', 'yesterday', or specify hours (e.g., '5 hours').")
            return
        messages = []

        async for message in channel.history(after=start_time, limit=1000):
            #let's ignore bot messages
            if not message.author.bot:
                messages.append(message.content)

        if len(messages) <= 1: # 1 because it counts the !tldr message
            await ctx.send(f"There's nothing to summarize from #{channel.name} within the timeframe you requested.")
            return
        else:
            summary = utils.chatgpt.summarize(messages)

        thread = await ctx.channel.create_thread(name=f"TLDR; for #{channel.name} ({time_frame})", type=discord.ChannelType.public_thread)
        await thread.send(summary)

    @bot.command()
    async def cmd(ctx, c):
        if ctx.author.name not in credentials.admin:
            ctx.command = bot.get_command("no")
            await bot.invoke(ctx)
            print(f"{ctx.author.name} tried to execute an unauthorized command")
            return

        match c:
            case 'refresh':
                if not restart_caching_event:
                    message = "No caching thread"
                    await ctx.send("No caching thread")
                    print(message)
                    return

                restart_caching_event.set()
                await ctx.send("restarting cache thread")
                return

    @bot.command(
        help=bot.command_prefix + "fuck <?name?>",
        extras={'meme': True}
    )
    async def fuck(ctx, *things):
        person = ' '.join(things)
        fuckEmbed = create_default_embed(color=discord.Color.red())
        fuckEmbed.set_thumbnail(
            url="https://avatars.githubusercontent.com/u/1737241?v=4")
        fuckEmbed.add_field(
            name=f'Fuck {person}', value=f'Get Fucked {person}')
        await ctx.send(embed=fuckEmbed)

    @bot.command(
        help=bot.command_prefix + "updog",
        extras={'meme': True}
    )
    async def updog(ctx):
        await ctx.send("what's up dog?")

    @bot.command(
        help=bot.command_prefix + "fmk <name> <name> <name>",
        extras={'meme': True}
    )
    async def fmk(ctx, person1=None, person2=None, person3=None):
        if person1 is None or person2 is None or person3 is None:
            await ctx.send("please send 3 names")
            return
        people = [person1, person2, person3]
        random.shuffle(people)
        fmkEmbed = create_default_embed(color=discord.Color.pink())
        fmkEmbed.set_thumbnail(
            url="https://pngimg.com/d/kim_jong_un_PNG37.png")
        fmkEmbed.add_field(
            name=f"Fuck {people[0]} \U0001F346", value=f"Get Fucked, {people[0]} ")
        fmkEmbed.add_field(
            name=f"Marry {people[1]} \U0001F48D", value=f"How sweet, {people[1]}")
        fmkEmbed.add_field(
            name=f"Kill {people[2]} \U0001F52A", value=f"I guess you'll just die, {people[2]}")

        await ctx.send(embed=fmkEmbed)

    @bot.command(
        help=bot.command_prefix + "stepcaptain",
        extras={'meme': True}
    )
    async def stepcaptain(ctx):
        await ctx.send('https://imgur.com/VJyQs2L')

    @bot.command(
        help=bot.command_prefix + "chirp <name> - can @ someone or just put a name",
        extras={'meme': True}
    )
    async def chirp(ctx, user=None):
        if user is None:
            await ctx.send("Give me someone to chirp!")
            return

        chirp = utils.chatgpt.ai_chirp(
            user, ctx.bot.extras['team_data']['teams'])

        await ctx.send(chirp)

    @bot.command(
        help=bot.command_prefix + "ruf :|",
        extras={'meme': True}
    )
    async def ruf(ctx):
        await ctx.send(file=discord.File('res/images/ruf.jpeg'))

    @bot.command(
        help=bot.command_prefix + "pat - god i miss that man",
        extras={'meme': True}
    )
    async def pat(ctx):
        count = None
        if ENABLE_REMOTE_STORAGE:
            count = extras['remote_storage_connection'].miss_pat()
        else:
            if 'pat' not in ctx.command.extras:
                pat_base_miss_score = 700
                ctx.command.extras['pat'] = random.randint(
                    pat_base_miss_score, pat_base_miss_score + 500)

            ctx.command.extras['pat'] += 1
            count = ctx.command.extras['pat']

        await ctx.send(f'Pat has been missed {count} times. We love you Pat!')

    @bot.command(
        extras={'meme': True}
    )
    async def goon(ctx):
        await ctx.send(file=discord.File('res/images/goon.jpg'))

    @bot.command(
        help=bot.command_prefix + "no",
        extras={'meme': True}
    )
    async def no(ctx):
        await ctx.send(file=discord.File('res/images/no.png'))

    @bot.command(
        help=bot.command_prefix + "male",
        extras={'meme': True}
    )
    async def male(ctx):
        await ctx.send(file=discord.File('res/images/male.jpg'))

    @bot.command(
        help=bot.command_prefix + "jamesriley",
        extras={'meme': True}
    )
    async def jamesriley(ctx):
        await ctx.send(file=discord.File('res/images/jamesriley.png'))

    @bot.command(
        help=bot.command_prefix + "love",
        extras={'meme': True}
    )
    async def love(ctx):
        await ctx.send(file=discord.File('res/images/love.png'))

    @bot.command(
        help=bot.command_prefix + "eepy",
        extras={'meme': True}
    )
    async def eepy(ctx):
        await ctx.send(file=discord.File('res/images/sleepy.jpg'))

    @bot.command(
        help=bot.command_prefix + "squats",
        extras={'meme': True}
    )
    async def squats(ctx):
        await ctx.send(file=discord.File('res/images/squats.png'))

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
