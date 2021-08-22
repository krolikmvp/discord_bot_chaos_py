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
    async def register(self, ctx, arg):
        if ctx.message.author.permissions_in(ctx.message.channel).administrator:

            if arg == "warframe":
                # Registers channel for the Warframe event notifications
                querry = f'INSERT INTO "warframe" ("author","channel_id","date","guild_name") VALUES (' \
                         f'"{ctx.message.author.name}", ' \
                         f'{ctx.message.channel.id}, ' \
                         f'"{datetime.datetime.now().strftime("%c")}", ' \
                         f'"{ctx.message.guild.name}")'

                await ctx.send(await self._register_item(querry))

            if arg == "bdo_reminder":
                # Registers channel for the Warframe event notifications
                querry = f'INSERT INTO "bdo_remind_channel" ("channel_id") VALUES ('f'{ctx.message.channel.id})'

                await ctx.send(await self._register_item(querry))

            if arg.startswith("insult"):

                mention = None
                print(ctx.message.mentions)
                try:
                    mention = ctx.message.mentions[0].id
                except IndexError as ex:
                    await ctx.send(f"Something went wrong. Message format may be incorrect. "
                                   f"You have to mention someone!")
                    self.logging.error(f"Error when adding insult: {ex}. Mentions: {ctx.message.mentions}")

                if mention:
                    await ctx.send(f"Great, now I will be very mean to <@{mention}>")
                    # Registers insult for the specific user on the specific channel
                    querry = f'INSERT INTO "insult" ("channel_id","target_id","insulted_day") VALUES (' \
                             f'"{ctx.message.channel.id}", ' \
                             f'"{mention}", ' \
                             f'"{0}")'
                    self.logging.debug(querry)
                    await ctx.send(await self._register_item(querry))
        else:
            await ctx.send("Not enough permissions, only Admin can register a channel")

    @commands.command(name="unregister", help="Unregister channel from an event subscription "
                                              "(warframe only for now)", pass_context=True)
    async def unregister_item(self, ctx, *arg):
        if ctx.message.author.permissions_in(ctx.message.channel).administrator:
            if not arg:
                await ctx.send("You need to select the item to unregister")
            else:
                if arg[0] == "warframe":
                    message = await self._unregister_channel('warframe', ctx.message.channel.id)
                    await ctx.send(message)
                elif arg[0] == "insult":
                    message = await self._unregister_item('insult', ctx.message.channel.id)
                    await ctx.send(message)
                else:
                    await ctx.send("Unknown item to unregister")
        else:
            await ctx.send("Not enough permissions, only Admin can unregister this item")

    @staticmethod
    async def _register_item(*args):

        try:
            with sqlite3.connect(DATABASE_NAME) as con:
                c = con.cursor()
                c.execute(args[0])
                con.commit()
                c.close()
        except sqlite3.IntegrityError as ex:
            response = "Unable to add item to the database. Item is probably already on the list"
            logging.error(f"Unable to add item to the database. {ex}")
        except Exception as exc:
            response = "Unable to add item to the database. Unknown error"
            logging.error(f"Unable to add item to the database. {exc}")
        else:
            response = "Item successfully registered"
        return response

    async def _unregister_querry(self, *args):
        querry_prefix = f'DELETE from '
        args_len = len(args)
        args_add = 3
        if args_len <= 2:
            raise RuntimeError("Not enough arguments")
        elif args_len % 2 == 0:
            raise RuntimeError("Invalid number of arguments")
        else:
            args_pairs = int((args_len - 1) / 2)
            querry_first_piece = f'{args[0]} where {args[1]} = {args[2]}'
            querry_last_piece = ''
            if args_pairs > 1:
                for i in range(0, args_pairs, 2):
                    querry_last_piece += f' AND {args[args_add + i]} = {args[args_add + i + 1]}'
            response = querry_prefix + querry_first_piece + querry_last_piece
        return response

    async def _unregister_item(self, *args):

        try:
            querry = self._unregister_querry(*args)
        except RuntimeError as re:
            return re

        try:
            with sqlite3.connect(DATABASE_NAME) as con:
                c = con.cursor()
                c.execute(querry)
                con.commit()
                c.close()
        except Exception as exc:
            response = "Unable to remove channel from the database. Unknown error"
            logging.error(f"Unable to remove channel from the database. {exc}")
        else:
            response = "Channel successfully unregistered"
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
