from discord.ext import commands, tasks
from discord import Embed
import discord
import logging
import asyncio
import aiohttp
import datetime
import sqlite3
from utils.load_config import DATABASE_NAME
from chaos import args

EVENT_REFRESH_TIMEOUT = 600 if not args.debug else 10


class Warframe(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.logging = logging.getLogger('chaos_logger')
        self.active_events = dict()
        self.active_alerts = dict()
        self.loaded_events = []
        self.new_events = []
        self.registered_channels = []
        self.notified_channels = []
        self.event_loop.start()

    @commands.Cog.listener()
    async def on_ready(self):
        await self.load_events()

    @commands.command(name="warframe_events", help="Shows active events in Warframe")
    async def post_events(self, message):
        await self.update_channels()
        if message.channel.id in self.registered_channels:
            await self.send_events(message.channel)
        else:
            await message.send("This channel is not registered for Warframe info")

    @tasks.loop(seconds=EVENT_REFRESH_TIMEOUT)
    async def event_loop(self):
        await self.update_channels()
        await self.get_events()
        await self.send_events_all_channels()
        await self.update_events()

    @event_loop.before_loop
    async def before_event_loop(self):
        await self.bot.wait_until_ready()

    async def get_alerts(self):
        #TODO
        async with aiohttp.ClientSession() as session:
            async with session.get('https://api.warframestat.us/pc/alerts') as r:
                if r.status == 200:
                    js = await r.json()
                    print(js)

    async def get_events(self):
        async with aiohttp.ClientSession() as session:
            async with session.get('https://api.warframestat.us/pc/events') as r:
                if r.status == 200:
                    js = await r.json()
                    for event in js:

                        event_id = str(event["id"])
                        print(f"Event {event_id}")
                        if event_id not in self.active_events.keys():
                            event_params = dict()
                            event_params["description"] = event.get("description", "None")
                            event_params["node"] = event.get("node", "None")
                            rewards = [r["itemString"] for r in event["rewards"] if len(r["itemString"]) > 1]
                            if not len(rewards):
                                rewards = [r["rewardPool"] for r in event["jobs"]]
                                rewards = rewards[0]
                            event_params["rewards"] = rewards
                            event_params["expired"] = event["expired"]
                            event_params["expiry"] = event["expiry"]
                            event_params["new"] = False
                            if event_id not in self.loaded_events:
                                self.new_events.append(event_id)
                                event_params["new"] = True
                            self.active_events[event_id] = event_params
                            self.logging.info(f"New Warframe event appeared: {self.active_events[event_id]}")
        self.logging.debug(f"Active events: {self.active_events}")

    async def send_events_all_channels(self):
        if self.new_events:
            for channel in self.registered_channels:
                ch = self.bot.get_channel(channel)
                await self.send_events(ch)
            self.logging.info(f"Events sent to all of the channels: {self.new_events}")
            self.new_events = []

    async def send_events(self, channel: discord.TextChannel):
        if not self.active_events:
            await channel.send("There are no active events")
        else:
            for event in self.active_events:
                await channel.send(embed=self.create_embed(self.active_events[event]))

    async def update_channels(self):
        self.logging.debug("Updating channels")
        with sqlite3.connect(DATABASE_NAME) as con:
            c = con.cursor()
            querry = c.execute('SELECT channel_id FROM warframe')
            for row in querry:
                if row[0] not in self.registered_channels:
                    self.registered_channels.append(row[0])
            c.close()
        self.logging.debug(f"Registered channels: {self.registered_channels}")

    def create_embed(self, event):
        new_event = "[NEW] " if event["new"] else ""

        title = new_event + event["description"]
        embed = Embed(
            color=0x247dc2,
            title=title,
            description=event["node"]
        )

        embed.add_field(name="Rewards", value=",".join(event["rewards"]), inline=False)
        embed.set_thumbnail(
            url="https://cdn.discordapp.com/attachments/791645870197309442/791645890360246302/d6zs6fz-101fece6-7a55-4af1-beda-33a3ffc43fc7.png")

        delta = str(self.get_expiration_time(event["expiry"]))
        delta_str = delta.rsplit(":", 1)[0] + ' hours left'
        embed.set_footer(text=delta_str)

        return embed

    async def update_events(self):
        for new_event in self.new_events[:]:
            if new_event not in self.loaded_events:
                self.loaded_events.append(new_event)

                with sqlite3.connect(DATABASE_NAME) as con:
                    c = con.cursor()
                    c.execute('INSERT INTO "warframe_events" ("event_id") VALUES (?)', (new_event,))
                    con.commit()
                    c.close()

        for active_event in self.active_events.keys():
            self.active_events[active_event]["new"] = False

        for loaded_event in self.loaded_events:
            if not self.active_events.get(loaded_event, False):
                await self.remove_expired_event(loaded_event)
            else:
                if self.active_events[loaded_event]["expired"]:
                    del self.active_events[loaded_event]

    async def load_events(self):

        with sqlite3.connect(DATABASE_NAME) as con:
            c = con.cursor()
            querry = c.execute('SELECT event_id FROM warframe_events')
            for row in querry:
                self.loaded_events.append(row[0])
            c.close()
        self.logging.debug(f"Loaded events: {self.loaded_events}")

    async def remove_expired_event(self, event_id: str):

        with sqlite3.connect(DATABASE_NAME) as con:
            c = con.cursor()
            c.execute(f'DELETE FROM warframe_events WHERE event_id="{event_id}"')
            con.commit()
            c.close()

        self.logging.info(f"Removed expired event: {event_id}")

    @staticmethod
    def get_expiration_time(expiration_time):
        """
        Function assumes expiration time format is : 2021-01-18T19:00:00.000Z
        :param expiration_time: string
        :return: deltatime object
        """
        time_now = datetime.datetime.now()
        expiration_d, expiration_h = expiration_time.split("T")
        exp_date = expiration_d.split('-')
        exp_date = [int(e) for e in exp_date]
        exp_hour = expiration_h.split(':')
        exp_hour = [int(e) for e in exp_hour[:2]]

        expiration_date = datetime.datetime(*exp_date, *exp_hour)
        delta = expiration_date - time_now

        return delta

    def cog_unload(self):
        self.event_loop.cancel()


def setup(bot):
    bot.add_cog(Warframe(bot))
