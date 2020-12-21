import os
import asyncio
import aiohttp
import discord
from discord.ext import commands
from utils.load_config import DATABASE_NAME
from utils.plot import StatPlot
import datetime
import logging
import sqlite3
import calendar

class Stats(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.logging = logging.getLogger('chaos_logger')
        
    @commands.command(pass_context=True, help="Creates a chart of todays messages")
    async def stats(self, message):

        date = datetime.datetime.now()

        month_num = int(date.strftime("%m"))
        day_num = int(date.strftime("%d"))
        year = int(date.strftime("%Y"))

        messages_today = 0
        hour_position = 5
        hours = dict()
        with sqlite3.connect(DATABASE_NAME) as con:
            c = con.cursor()
            querry = c.execute('SELECT * FROM stats WHERE month_num=? AND day_num=? AND year=?', (month_num, day_num, year))
            for row in querry:
                hours[str(row[hour_position])] = hours.get(str(row[hour_position]), 1) + 1
                messages_today += 1

            c.close()

        graph_dict = dict()
        for i in range(0,24):
            index = str(i)
            graph_dict[index] = graph_dict.get(index, 0)
            if index in hours:
                graph_dict[index] = hours[index]

        self.logging.debug(f"Hours dict: {hours}")
        self.logging.debug(f"Graph dict: {graph_dict}")
        self.logging.debug(f"messages today: {messages_today}")

        plot = StatPlot(graph_dict)
        await message.send(file=discord.File(plot.plot_day_stats()))


    @commands.command(pass_context=True, help="Creates a chart of this months messages")
    async def stats_month(self, message):

        date = datetime.datetime.now()

        month_num = int(date.strftime("%m"))
        year = int(date.strftime("%Y"))

        days_this_month = calendar.monthrange(date.year, date.month)[1]
        messages_month = 0
        day_position = 2
        days = dict()
        with sqlite3.connect(DATABASE_NAME) as con:
            c = con.cursor()
            querry = c.execute('SELECT * FROM stats WHERE month_num=? AND year=?', (month_num, year))
            for row in querry:
                days[str(row[day_position])] = days.get(str(row[day_position]), 1) + 1
                messages_month += 1
            c.close()

        graph_dict = dict()
        for i in range(1, days_this_month+1):
            index = str(i)
            graph_dict[index] = graph_dict.get(index, 0)
            if index in days:
                graph_dict[index] = days[index]

        self.logging.debug(f"Days dict: {days}")
        self.logging.debug(f"Graph dict: {graph_dict}")
        self.logging.debug(f"messages this month: {messages_month}")

        plot = StatPlot(graph_dict)
        await message.send(file=discord.File(plot.plot_month_stats()))


    @commands.Cog.listener()
    async def on_message(self, message):
        if not message.author.bot:
            date = datetime.datetime.now()

            month_num = int(date.strftime("%m"))
            day_num = int(date.strftime("%d"))
            day_week = int(date.strftime("%w"))
            year = int(date.strftime("%Y"))
            hour = int(date.strftime("%H"))

            with sqlite3.connect(DATABASE_NAME) as con:
                c = con.cursor()
                c.execute('INSERT INTO "stats" ("author" , "month_num" , "day_num" , "day_week" , "year" , "hour") VALUES (?, ?, ?, ?, ?, ?)', (message.author.name, month_num, day_num, day_week, year, hour))
                con.commit()
                c.close()


def setup(bot):
    bot.add_cog(Stats(bot))