from datetime import datetime, timedelta
from discord.ext import commands, tasks
from asyncio import TimeoutError
from random import choice, seed
from time import time
from utils import db
import discord
import logging

logger = logging.getLogger(__name__)

def convert(time):
    pos = ["m", "h", "d"]
    time_dict = {"m": 60, "h": 3600, "d": 24*3600}
    unit = time[-1]
    if unit not in pos:
        return -1
    try:
        timeVal = int(time[:-1])
    except Exception as e:
        return -2

    return timeVal*time_dict[unit]

def create_giveaway_embed(author, prize):
    embed = discord.Embed(title=":tada: Giveaway :tada:",
                    description=f"Win **{prize}**!",
                    colour=0x00FFFF)
    embed.add_field(name="Hosted By:", value=author.mention)
    return embed

def winning_text(prize, winner):
    return f'Congratulations {winner.mention}! You won **{prize}**!'

def checkIfActiveGiveaways():
    giveaways = db.session.query(db.active_giveaways).all()
    if len(giveaways) > 0:
        return True
    return False

class Giveaway(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.cancelled = False
        if checkIfActiveGiveaways():
            self.giveaway_task.start()

    @commands.group()
    async def giveaway(self, ctx):
        pass

    @giveaway.command()
    async def create(self, ctx):
        if not await self.has_permissions(ctx):
            return

        # Ask Questions
        questions = ["Setting up your giveaway. Choose what channel you want your giveaway in?",
                     "For How long should the Giveaway be hosted ? type number followed (m|h|d). Example: `10m`",
                     "What is the Prize?"]
        answers = []

        # Check Author
        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel

        for i, question in enumerate(questions):
            embed = discord.Embed(title=f"Question {i}",
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
        except Exception as e:
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
        embed = create_giveaway_embed(ctx.author, prize)
        embed.description += "\nReact with :tada: to enter!"
        end = (datetime.now() + timedelta(seconds=time))
        end_string = end.strftime('%d.%m.%Y %H:%M')
        embed.set_footer(text=f"Giveway ends on {end_string}")
        newMsg = await channel.send(embed=embed)
        creator = ctx.author
        await newMsg.add_reaction("🎉")
        db.session.add(db.active_giveaways(creator, end, prize, newMsg))
        db.session.commit()

        self.giveaway_task.start()

    @giveaway.command()
    async def reroll(self, ctx, channel: discord.TextChannel, id_: int):
        if not await self.has_permissions(ctx):
            return
        try:
            msg = await channel.fetch_message(id_)
        except Exception as e:
            await ctx.send("The channel or ID mentioned was incorrect")
            return
        users = await msg.reactions[0].users().flatten()
        users.pop(users.index(self.bot.user))
        prize = await self.get_giveaway_prize(ctx, channel, id_)
        embed = create_giveaway_embed(ctx.author, prize)
        if len(users) <= 0:
            embed.set_footer(text="No one won the Giveaway")
        elif len(users) > 0:
            winner = choice(users)
            embed.add_field(name=f"Congratulations on winning {prize}", value=winner.mention)
            await channel.send(winning_text(prize, winner))

        await msg.edit(embed=embed)

    @giveaway.command()
    async def stop(self, ctx, channel: discord.TextChannel, id_: int):
        if not await self.has_permissions(ctx):
            return
        try:
            msg = await channel.fetch_message(id_)
            newEmbed = discord.Embed(title="Giveaway Cancelled", description="The giveaway has been cancelled!!")
            # Set Giveaway cancelled
            self.cancelled = True
            await msg.edit(embed=newEmbed)
        except Exception as e:
            embed = discord.Embed(title="Failure!", description="Cannot cancel Giveaway")
            await ctx.send(emebed=embed)

    @tasks.loop(seconds=45.0)
    async def giveaway_task(self):
        giveaways = db.session.query(db.active_giveaways).all()
        random_seed_value = time()
        for giveaway in giveaways:
            if datetime.now() >= giveaway.end_date:
                channel = self.bot.get_channel(giveaway.channel_id)
                message = await channel.fetch_message(giveaway.message_id)
                users = await message.reactions[0].users().flatten()
                author = await self.bot.fetch_user(giveaway.creator_user_id)
                prize = giveaway.prize
                embed = create_giveaway_embed(author, prize)

                users.pop(users.index(self.bot.user))
                # Check if User list is not empty
                if len(users) <= 0:
                    embed.remove_field(0)
                    embed.set_footer(text="No one won the Giveaway")
                    await channel.send('No one won the Giveaway')
                elif len(users) > 0:
                    seed(random_seed_value)
                    winner = choice(users)
                    random_seed_value += 1
                    embed.add_field(name=f"Congratulations on winning {prize}", value=winner.mention)
                    await channel.send(winning_text(prize, winner))
                await message.edit(embed=embed)
                db.session.query(db.active_giveaways).filter_by(message_id=message.id).delete()
                db.session.commit()

    async def get_giveaway_prize(self, ctx, channel: discord.TextChannel, id_: int):
        try:
            msg = await channel.fetch_message(id_)
        except Exception as e:
            await ctx.send("The channel or ID mentioned was incorrect")
        return msg.embeds[0].description.split("Win ")[1].split(" today!")[0]

    async def has_permissions(self, ctx):
        if not ctx.channel.permissions_for(ctx.author).manage_channels and not await self.bot.is_owner(ctx.author):
            await ctx.send("You don't have permissions to do that", delete_after=10)
            return False
        return True


def setup(bot):
    bot.add_cog(Giveaway(bot))
