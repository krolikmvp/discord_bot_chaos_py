import discord
import argparse
import sqlite3
from discord.ext import commands
from utils.load_cogs import cogs
from utils.load_config import TOKEN, GUILD,COMMANDS_PREFIX, DATABASE_NAME
import logging
from logging.handlers import RotatingFileHandler

# logger, parser and bot config
parser = argparse.ArgumentParser()
parser.add_argument('-m', '--show_members', action='store_true', default=False,
                    help='Shows members of your guild (config.json)')
parser.add_argument('-d', '--debug', action='store_true', default=False, help='Runs bot with debug loggin on')
args = parser.parse_args()

intents = discord.Intents.default()
intents.members = True
bot = commands.Bot(command_prefix=COMMANDS_PREFIX, intents=intents)

log_level = logging.INFO if not args.debug else logging.DEBUG
log_formatter = logging.Formatter('%(asctime)s %(levelname)s %(funcName)s(line: %(lineno)d) %(message)s')
logFile = 'logfile.log'
my_handler = RotatingFileHandler(logFile, mode='a', maxBytes=5*1024*1024, backupCount=2, encoding=None, delay=0)
my_handler.setFormatter(log_formatter)
my_handler.setLevel(log_level)
chaos_log = logging.getLogger('chaos_logger')
chaos_log.setLevel(log_level)
chaos_log.addHandler(my_handler)

# Load all cogs
for cog in cogs:
    try:
        bot.load_extension(cog)
    except Exception as ex:
        print(f'Could not load cog {cog}')
        chaos_log.error(f'Could not load cog {cog}')


@bot.event
async def on_ready():
    # List all servers where the bot is present 
    print(f'{bot.user} is connected to the following guilds:\n')
    for guild in bot.guilds:
        print("Guild:")
        print(f'{guild.name}(id: {guild.id})')

        # Your server members
        if guild.name == GUILD and args.show_members:
            print('Guild Members:')
            for member in guild.members:
                name, id_ = member.name, member.id
                print(f'{name} (id: {str(id_)})')
    setup_database(DATABASE_NAME)


# Main message handle function. Message is further processed in cog classes
@bot.event
async def on_message(message):
    if message.author.bot:
        return
    if isinstance(message.channel, discord.DMChannel):
        await message.author.send('Sorry, but I don\'t accept commands through direct messages!')
        return
    await bot.process_commands(message)


def setup_database(db):
    chaos_log.info("Creating database columns")
    with sqlite3.connect(db) as con:
        c = con.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS `quotes` (
                    `id`	INTEGER PRIMARY KEY AUTOINCREMENT,
                    `quote`	TEXT NOT NULL,
                    `time`	TEXT NOT NULL,
                    `author`    TEXT NOT NULL,
                    `author_id`    INTEGER NOT NULL
                    );''')
        c.execute('''CREATE TABLE IF NOT EXISTS `stats` (
                    `author`	TEXT NOT NULL,
                    `month_num`	INTEGER NOT NULL,
                    `day_num`	INTEGER NOT NULL,
                    `day_week`	INTEGER NOT NULL,
                    `year`	INTEGER NOT NULL,
                    `hour`	INTEGER NOT NULL
                    );''')
        # c.execute('''DROP TABLE  `warframe`''')
        c.execute('''CREATE TABLE IF NOT EXISTS `warframe` (
                    `author`	TEXT NOT NULL,
                    `channel_id`	INTEGER PRIMARY KEY NOT NULL,
                    `date`	TEXT NOT NULL,
                    `guild_name`	TEXT NOT NULL
                    );''')
        # c.execute('''DROP TABLE  `warframe_events`''')
        c.execute('''CREATE TABLE IF NOT EXISTS `warframe_events` (
                    `event_id`	TEXT PRIMARY KEY NOT NULL
                    );''')
        c.execute('''CREATE TABLE IF NOT EXISTS `warframe_notify_channel` (
                    `channel_id`	INTEGER NOT NULL,
                    `notified`      INTEGER NOT NULL,
                    FOREIGN KEY (channel_id) REFERENCES `warframe` (channel_id)
                        ON UPDATE CASCADE
                        ON DELETE CASCADE
                    );''')
        # c.execute('''DROP TABLE  `insult`''')
        c.execute('''CREATE TABLE IF NOT EXISTS `insult` (
                    `id`	INTEGER PRIMARY KEY AUTOINCREMENT,
                    `channel_id`	INTEGER NOT NULL,
                    `target_id`	INTEGER NOT NULL,
                    `insulted_day`	INTEGER NOT NULL,
                    UNIQUE(channel_id, target_id)
                    );''')
        c.execute('''CREATE TABLE IF NOT EXISTS `bdo_remind_channel` (
                    `channel_id`	INTEGER PRIMARY KEY
                    );''')
        c.execute('''CREATE TABLE IF NOT EXISTS `bdo_remind_user` (
                    `channel_id`	INTEGER PRIMARY KEY,
                    `author`	TEXT NOT NULL,
                    `hour`	INTEGER NOT NULL,
                    `active`	INTEGER NOT NULL,
                    UNIQUE(channel_id, author)
                    );''')
        con.commit()
        c.close()


bot.run(TOKEN)
