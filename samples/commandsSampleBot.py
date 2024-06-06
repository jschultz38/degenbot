import discord
from discord.ext import commands
from credentials import test_token

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

@bot.command()
async def schedule(ctx):
    await ctx.send('tbd')

bot.run(test_token)
