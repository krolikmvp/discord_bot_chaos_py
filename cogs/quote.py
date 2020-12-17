import os
import asyncio
import aiohttp
import discord
from discord.ext import commands
from utils.load_config import QUOTE_AUTHORS_ID
import datetime

class Quote(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        #if message.author.id in QUOTE_AUTHORS_ID and ( 256 > len(message) > 5):
        print(message.author.id)
        print(message.content)
        date = datetime.datetime.now()
        weekday = int(date.strftime("%w"))
        hour = date.hour
        day_range = range(0,7)#range(1,6)
        hour_range = range(0,24)#range(7,16)
        
        # 0 is Sunday 6 is Saturday
        # check if message is sent between Monday and Friday and hour is 7-15
        if weekday in day_range and hour in hour_range:
            #TODO check if there are no  mentions or if they are stored correctly <@!353122126695497738>
            #TODO check if there are links
            pass
        # if (args[0] != 'pls')
        # {
        #     insertQuote(sql,message.content)
        # }

def setup(bot):
    bot.add_cog(Quote(bot))