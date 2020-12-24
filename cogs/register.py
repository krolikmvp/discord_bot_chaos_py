from discord.ext import commands
import logging
import sqlite3
import datetime
from utils.load_config import DATABASE_NAME


class Register(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.logging = logging.getLogger('chaos_logger')

    @commands.command(name="register", help="Register channel for an event subscription"
                                            " (warframe only for now)", pass_context=True)
    async def register_channel(self, ctx, arg):
        if ctx.message.author.permissions_in(ctx.message.channel).administrator:

            if arg == "warframe":
                querry = f'INSERT INTO "warframe" ("author","channel_id","date","guild_name") VALUES (' \
                         f'"{ctx.message.author.name}", ' \
                         f'{ctx.message.channel.id}, ' \
                         f'"{datetime.datetime.now().strftime("%c")}", ' \
                         f'"{ctx.message.guild.name}")'

                await ctx.send(await self._register_channel(querry))

        else:
            await ctx.send("Not enough permissions, only Admin can register a channel")

    @commands.command(name="unregister", help="Unregister channel from an event subscription "
                                              "(warframe only for now)", pass_context=True)
    async def unregister_channel(self, ctx, arg):
        if ctx.message.author.permissions_in(ctx.message.channel).administrator:
            if arg == "warframe":
                await ctx.send(await self._unregister_channel('warframe', ctx.message.channel.id))
        else:
            await ctx.send("Not enough permissions, only Admin can unregister a channel")

    async def _register_channel(self, *args, **kwargs):

        try:
            with sqlite3.connect(DATABASE_NAME) as con:
                c = con.cursor()
                c.execute(args[0])
                con.commit()
                c.close()
        except sqlite3.IntegrityError as ex:
            response = "Unable to add channel to the database. Channel is probably already on the list"
            logging.error(f"Unable to add channel to the database. {ex}")
        except Exception as exc:
            response = "Unable to add channel to the database. Unknown error"
            logging.error(f"Unable to add channel to the database. {exc}")
        else:
            response = "Channel successfully registered"
        return response

    async def _unregister_channel(self, table_name, channel_id):
        try:
            with sqlite3.connect(DATABASE_NAME) as con:
                c = con.cursor()
                c.execute(f"DELETE from {table_name} where channel_id = {channel_id}")
                con.commit()
                c.close()
        except Exception as exc:
            response = "Unable to remove channel from the database. Unknown error"
            logging.error(f"Unable to remove channel from the database. {exc}")
        else:
            response = "Channel successfully unregistered"
        return response


def setup(bot):
    bot.add_cog(Register(bot))
