from asyncio import TimeoutError, sleep
from datetime import datetime, timedelta
from os import name
from random import choice

import discord
import logging
from discord import Embed
from discord.ext import commands
from discord.ext.commands import command


def convert(time):
    pos = ["s", "m", "h", "d"]
    time_dict = {"s": 1, "m": 60, "h": 3600, "d": 24*3600}
    unit = time[-1]
    if unit not in pos:
        return -1
    try:
        timeVal = int(time[:-1])
    except:
        return -2

    return timeVal*time_dict[unit]

def create_giveaway_embed(ctx, prize):
    embed = Embed(title=":tada: Giveaway :tada:",
                    description=f"Win **{prize}** today!",
                    colour=0x00FFFF)
    embed.add_field(name="Hosted By:", value=ctx.author.mention)
    return embed

def winning_text(prize, winner):
    return f'Congratulations {winner.mention}! You won **{prize}**!'

class Giveaway(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.cancelled = False

    @command(name="giveawaycreate", aliases=["gcreate", "gcr"])
    async def create_giveaway(self, ctx):
        if not await self.has_permissions(ctx):
            return

        # Ask Questions
        questions = ["Setting up your giveaway. Choose what channel you want your giveaway in?",
                     "For How long should the Giveaway be hosted ? type number followed (s|m|h|d). Example: `10m`",
                     "What is the Prize?"]
        answers = []

        # Check Author
        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel

        for i, question in enumerate(questions):
            embed = Embed(title=f"Question {i}",
                          description=question)
            await ctx.send(embed=embed)
            try:
                message = await self.bot.wait_for('message', timeout=45, check=check)
            except TimeoutError:
                await ctx.send("You didn't answer the questions in Time")
                return
            answers.append(message.content)

        # Check if Channel Id is valid
        try:
            channel_id = int(answers[0][2:-1])
        except:
            await ctx.send(f"The Channel provided was wrong. The channel should be {ctx.channel.mention}")
            return

        channel = self.bot.get_channel(channel_id)
        time = convert(answers[1])
        # Check if Time is valid
        if time == -1:
            await ctx.send("The Time format was wrong")
            return
        elif time == -2:
            await ctx.send("The Time was not conventional number")
            return
        prize = answers[2]

        await ctx.send(f"Setup finished. Giveaway for **'{prize}'** will be in {channel.mention}")
        embed = create_giveaway_embed(ctx, prize)
        embed.description += "\nReact with :tada: to enter!"
        end = (datetime.now() + timedelta(seconds=time)).strftime('%d.%m.%Y %H:%M:%S')
        embed.set_footer(text=f"Giveway ends on {end}")
        newMsg = await channel.send(embed=embed)
        await newMsg.add_reaction("🎉")
        # Check if Giveaway Cancelled
        self.cancelled = False
        await sleep(time)
        if not self.cancelled:
            myMsg = await channel.fetch_message(newMsg.id)

            users = await myMsg.reactions[0].users().flatten()
            users.pop(users.index(self.bot.user))
            embed = create_giveaway_embed(ctx, prize)
            # Check if User list is not empty
            if len(users) <= 0:
                embed.set_footer(text="No one won the Giveaway")
                return
            elif len(users) > 0:
                winner = choice(users)
                embed.add_field(name=f"Congratulations on winning {prize}", value=winner.mention)
                await channel.send(winning_text(prize, winner))
            await myMsg.edit(embed=embed)

    @command(name="givereroll", aliases=["givrrl", "grr"])
    async def giveaway_reroll(self, ctx, channel: discord.TextChannel, id_: int):
        if not await self.has_permissions(ctx):
            return
        try:
            msg = await channel.fetch_message(id_)
        except:
            await ctx.send("The channel or ID mentioned was incorrect")
            return
        users = await msg.reactions[0].users().flatten()
        users.pop(users.index(self.bot.user))
        prize = await self.get_giveaway_prize(ctx, channel, id_)
        embed = create_giveaway_embed(ctx, prize)
        if len(users) <= 0:
            embed.set_footer(text="No one won the Giveaway")
        elif len(users) > 0:
            winner = choice(users)
            embed.add_field(name=f"Congratulations on winning {prize}", value=winner.mention)
            await channel.send(winning_text(prize, winner))

        await msg.edit(embed=embed)

    @command(name="givdel", aliases=["giftdel", "gdl"])
    async def giveaway_stop(self, ctx, channel: discord.TextChannel, id_: int):
        if not await self.has_permissions(ctx):
            return
        try:
            msg = await channel.fetch_message(id_)
            newEmbed = Embed(title="Giveaway Cancelled", description="The giveaway has been cancelled!!")
            # Set Giveaway cancelled
            self.cancelled = True
            await msg.edit(embed=newEmbed)
        except:
            embed = Embed(title="Failure!", description="Cannot cancel Giveaway")
            await ctx.send(emebed=embed)

    async def get_giveaway_prize(self, ctx, channel: discord.TextChannel, id_: int):
        try:
            msg = await channel.fetch_message(id_)
        except:
            await ctx.send("The channel or ID mentioned was incorrect")
        return msg.embeds[0].description.split("Win ")[1].split(" today!")[0]

    async def has_permissions(self, ctx):
        if not ctx.channel.permissions_for(ctx.author).manage_channels and not await self.bot.is_owner(ctx.author):
            await ctx.send("You don't have permissions")
            return False
        return True


def setup(bot):
    bot.add_cog(Giveaway(bot))