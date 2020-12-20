import os
import asyncio
import aiohttp
import discord
from discord.ext import commands
from utils.load_config import QUOTE_AUTHORS_ID, DATABASE_NAME, COMMANDS_PREFIX, OWNER_ID
import datetime
import logging
import sqlite3

class Quote(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.forbidden_characters = ['<@!', 'http', 'www']
        self.start_commands = ['pls','<:', COMMANDS_PREFIX]
        self.quotes_dump_filename = 'quotes_dump.txt'
        self.minimum_message_length = 5
        self.maximum_message_length = 256

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.id in QUOTE_AUTHORS_ID and ( self.maximum_message_length > len(message) > self.minimum_message_length):
            date = datetime.datetime.now()
            quote_date = date.strftime("%c")
            weekday = int(date.strftime("%w"))
            hour = date.hour
            day_range = range(1,6)
            hour_range = range(7,16)

            # 0 is Sunday 6 is Saturday
            # check if message is sent between Monday and Friday and hour is 7-15
            if weekday in day_range and hour in hour_range:
                if not any ( characters in message.content for characters in self.forbidden_characters):
                    if not any (message.content.startswith(characters) for characters in self.start_commands):
                        self.insert_quote(message.content, quote_date, str(message.author.name))
                        logging.info("Quote added. Author: {}, time: {}, quote char length: {}".format(message.author, quote_date, len(message.content)))


    @commands.command(pass_context=True, help="Dumps all of the quotes of provided user from database to user_quotes_dump.txt file")
    async def log_quotes(self, ctx, arg):
        if str(ctx.message.author.id) == OWNER_ID:
            logging.info(f"Quotes dump process starts for user {arg}")
            with sqlite3.connect(DATABASE_NAME) as con:
                c = con.cursor()
                querry = c.execute('SELECT * FROM quotes WHERE author=?',[arg])
                rowcount = len(querry.fetchall())
                logging.debug(f"Rows count for user {arg}: {rowcount}")
                if rowcount:
                    with open(arg + '_' + self.quotes_dump_filename, "w+") as quote:
                        for row in c.execute('SELECT * FROM quotes WHERE author=?',[arg]):
                            try:
                                line = "".join(str(row)[1:-1])+'\n'
                                logging.debug(f"Line to write: {line}")
                                quote.write(line)
                            except Exception as ex:
                                logging.error(f"Error during quote dump: {ex}")
                        else:
                            await ctx.send(f"{arg} quotes dumped to file")
                else:
                    await ctx.send(f"Quotes from user {arg} not found")

                c.close()
            logging.info("Quotes dump process ended")
        else:
            logging.warning(f"{ctx.message.author} tried to use owner only function")

    def insert_quote(self, quote, time, author):
            with sqlite3.connect(DATABASE_NAME) as con:
                c = con.cursor()
                c.execute('INSERT INTO "quotes" ("quote","time","author") VALUES (?, ?, ?)', (quote, time, author))
                con.commit()
                c.close()


def setup(bot):
    bot.add_cog(Quote(bot))