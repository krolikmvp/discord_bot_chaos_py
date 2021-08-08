from discord.ext import commands, tasks
import logging
import random
import aiohttp
import sqlite3
from utils.load_config import DATABASE_NAME
import datetime
from chaos import args

INSULT_TIMER_SECONDS = 3600 if not args.debug else 2
INSULT_CHANCE = 0.1 if not args.debug else 0.7
INSULT_HOUR_RANGE = range(9, 21) if not args.debug else range(0, 24)


class Insult(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.logging = logging.getLogger('chaos_logger')
        self.insulted_day = None
        self._insult_loop.start()

    @tasks.loop(seconds=INSULT_TIMER_SECONDS)
    async def _insult_loop(self):
        date = datetime.datetime.now()
        hour = date.hour
        day = date.day
        # check if the time is between hour_range
        if hour in INSULT_HOUR_RANGE:

            insult_targets = self._get_all_records()
            for target in insult_targets:
                # was insulted today?
                if target["insulted_day"] != day:
                    roll = random.random()
                    # x% chances to insult each INSULT_TIMER_SECONDS
                    if roll < INSULT_CHANCE:
                        insult = await self._get_insult()
                        self.insulted_day = day

                        await self._insult(insult, target, day)

    async def _insult(self, insult, target, day):
        self._update_database(target, day)
        ch = self.bot.get_channel(target["channel"])
        await ch.send(f"<@{target['target']}> {insult}")

    def _get_all_records(self) -> list:
        records = []
        with sqlite3.connect(DATABASE_NAME) as con:
            c = con.cursor()
            querry = c.execute('SELECT * FROM insult')
            for row in querry:
                r = {"id": row[0], "channel": row[1], "target": row[2], "insulted_day": row[3]}
                records.append(r)
            c.close()
        return records

    def _update_database(self, target, day):
        with sqlite3.connect(DATABASE_NAME) as con:
            c = con.cursor()
            querry = f'UPDATE insult SET insulted_day = {day} WHERE id == {target["id"]}'
            c.execute(querry)
            c.close()

    @_insult_loop.before_loop
    async def _before_insult_loop(self):
        await self.bot.wait_until_ready()

    async def _get_insult(self):
        async with aiohttp.ClientSession() as session:
            async with session.get('https://evilinsult.com/generate_insult.php?lang=en&type=json') as r:
                if r.status == 200:
                    js = await r.json()
                    return js["insult"]
                else:
                    self.logging.error("Unable to get the insult from the API")
                    self.logging.error(r)
                    return "Have a nice day!"


def setup(bot):
    bot.add_cog(Insult(bot))
