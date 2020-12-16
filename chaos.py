import os
import discord
import json
from discord.ext import commands
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('-m','--show_members', action='store_true', default=False, help='Shows members of your guild (config.json)')

args = parser.parse_args()

intents = discord.Intents.default()
intents.members = True


## Read config file
config = None
with open('./config.json') as cfg:
    config = json.load(cfg)
TOKEN = config['token']
GUILD = config['guild']


bot = commands.Bot(command_prefix='!', intents=intents)


# ## List all servers where the bot is present 
@bot.event
async def on_ready():
    f'{bot.user} is connected to the following guilds:\n'
    for guild in bot.guilds:
        print("Guild:")
        print(f'{guild.name}(id: {guild.id})')

        # Your server members
        if guild.name == GUILD and args.show_members:
            print('Guild Members:')
            for member in guild.members:
                name, id = member.name, member.id
                print('{} (id: {})'.format(name, str(id)))

@bot.event
async def on_message(message):
    if message.author.bot:
        return
    if isinstance(message.channel, discord.DMChannel):
        await message.author.send('Sorry, but I don\'t accept commands through direct messages!')
        return
    if bot.dev and not await bot.is_owner(message.author):
        return
    await bot.process_commands(message)

bot.run(TOKEN)
