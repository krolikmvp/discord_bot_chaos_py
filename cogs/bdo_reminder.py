from discord.ext import commands, tasks
import logging
import random
import aiohttp
import sqlite3
from utils.load_config import DATABASE_NAME
import datetime
from chaos import args

CHECK_TIME_LOOP = 60 if not args.debug else 5
# Imperial delivery occurs every 3 hours. The first one starts at 2 AM, last 11 PM. That's 8 deliveries per day

# If the imperial delivery time start changes then change this value
DELIVERY_START = 2
# If the imperial delivery cooldown changes then change this value
DELIVERY_COOLDOWN = 3
# -1 hour because we want to sent the reminder before the delivery starts
DELIVERY_HOURS = [i*DELIVERY_COOLDOWN+(DELIVERY_START-1) for i in range(8)]
# Reminder time - minute
DELIVERY_MINUTE = 58


class BdoReminder(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.logging = logging.getLogger('chaos_logger')
        self.insulted_day = None
        self._reminder_loop.start()

    @tasks.loop(seconds=CHECK_TIME_LOOP)
    async def _reminder_loop(self):
        date = datetime.datetime.now()
        hour = date.hour
        if hour in DELIVERY_HOURS:
            if date.minute == DELIVERY_MINUTE:
                registered_channels = self._get_all_channels()
                for channel in registered_channels:
                    print(channel)
                    #await self._remind(channel)
        if args.debug:
            registered_channels = self._get_all_channels()
            for channel in registered_channels:
                await self._remind(channel)

    @_reminder_loop.before_loop
    async def _before_reminder_loop(self):
        await self.bot.wait_until_ready()

    async def _remind(self, channel):
        ch = self.bot.get_channel(channel)
        time = f"in {60-DELIVERY_MINUTE} minutes" if DELIVERY_MINUTE < 60 else "now"
        await ch.send(f"Imperial delivery starts {time}! @here")

    def _get_all_channels(self) -> list:
        records = []
        with sqlite3.connect(DATABASE_NAME) as con:
            c = con.cursor()
            querry = c.execute('SELECT * FROM bdo_remind_channel')
            for row in querry:
                records.append(row[0])
            c.close()
        return records


def setup(bot):
    bot.add_cog(BdoReminder(bot))
