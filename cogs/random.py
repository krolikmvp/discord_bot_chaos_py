import os
import asyncio
import aiohttp
import discord
from discord.ext import commands
from discord import Embed
import logging
from utils.load_config import QUOTE_AUTHORS_NAMES, DATABASE_NAME, COMMANDS_PREFIX, OWNER_ID, RANDOM_QUOTE_CUSTOM_NAME
import datetime
import sqlite3
import random


class Random(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.logging = logging.getLogger('chaos_logger')

    @commands.command(name="roll", help="Splits voice channel users into 2 teams", pass_context=True)
    async def team_voice_channel_users(self, ctx):
        self.logging.info("{ctx.message.author} requested voice channel team rolls")
        if not ctx.message.author.voice:
            await ctx.send("You have to be on the voice channel to use this command")
            return

        channel = ctx.message.author.voice.channel 
        channel_users = channel.members
        channel_member_names = [user.name for user in channel_users]
        if len(channel_member_names) % 2 != 0:
            channel_member_names.append('FREE SLOT')

        team_size = int(len(channel_member_names)/2)
        random.shuffle(channel_member_names)
        
        team1 = "\n".join(channel_member_names[0:team_size])
        team2 = "\n".join(channel_member_names[team_size:])
        
        embed = Embed(
            colour = 12331111,
            title = ' '
        )

        self.logging.info("Team1 rolled: {team1} ")
        self.logging.info("Team2 rolled: {team2} ")
        embed.add_field(name = 'Team 1:', value =  team1)
        embed.add_field(name = 'Team 2:', value =  team2)
        await ctx.send(embed = embed)


def setup(bot):
    bot.add_cog(Random(bot))