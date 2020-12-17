import os
import discord
import json
import argparse
from discord.ext import commands
from utils.load_cogs import cogs
from utils.load_config import TOKEN, GUILD,COMMANDS_PREFIX

parser = argparse.ArgumentParser()
parser.add_argument('-m','--show_members', action='store_true', default=False, help='Shows members of your guild (config.json)')
args = parser.parse_args()

intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(command_prefix=COMMANDS_PREFIX, intents=intents)


@bot.event
async def on_ready():
    # Load all cogs
    for cog in cogs:
        try:
            bot.load_extension(cog)
        except Exception:
            print(f'Couldn\'t load cog {cog}')
    # List all servers where the bot is present 
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

# Main message handle function. Message is further processed in cog classes
@bot.event
async def on_message(message):
    if message.author.bot:
        return
    if isinstance(message.channel, discord.DMChannel):
        await message.author.send('Sorry, but I don\'t accept commands through direct messages!')
        return
    await bot.process_commands(message)


bot.run(TOKEN)
