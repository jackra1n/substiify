from discord.ext import commands

from utils.store import store
from utils import db

import discord
import logging
import json

import numpy as np

logger = logging.getLogger(__name__)

class Votes(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.upvote_emote = ':this:877668616810692608'
        self.downvote_emote = ':that:877668628261126144'
        self.vote_channels = np.array(self.load_vote_channels())
        with open(store.settings_path, "r") as settings:
            self.settings = json.load(settings)

    def load_vote_channels(self) -> list:
        channel_array = []
        for entry in db.session.query(db.vote_channels).all():
            channel_array = np.append(channel_array, entry.channel_id)
        return channel_array

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.channel.id in self.vote_channels and not message.author.bot:
            await message.add_reaction(f'<{self.upvote_emote}>')
            await message.add_reaction(f'<{self.downvote_emote}>')

    @commands.group()
    async def votes(self, ctx):
        if ctx.invoked_subcommand is None and await self.has_permissions(ctx):
            await ctx.message.delete()
            if ctx.channel.id in self.vote_channels:
                embed = discord.Embed(description=f'Votes are **ALREADY enabled** in {ctx.channel.mention}!', colour=0x23b40c)
                await ctx.send(embed=embed, delete_after=10)
            else:
                embed = discord.Embed(description=f'Votes are **NOT enabled** in {ctx.channel.mention}!', colour=0xf66045)
                await ctx.send(embed=embed, delete_after=10)

    @votes.command()
    async def setup(self, ctx, channel: discord.TextChannel = None):
        if not await self.has_permissions(ctx):
            return
        await ctx.message.delete()
        channel = ctx.channel if channel is None else channel
        if channel.id not in self.vote_channels:
            self.vote_channels = np.append(self.vote_channels, channel.id)
        if db.session.query(db.vote_channels).filter_by(server_id=ctx.guild.id).filter_by(channel_id=channel.id).first() is None:
            db.session.add(db.vote_channels(ctx.guild.id, channel.id))
            db.session.commit()
        else:
            embed = discord.Embed(
                description=f'Votes are **already active** in {ctx.channel.mention}!',
                colour=0x23b40c
            )
            await ctx.send(embed=embed, delete_after=20)
            return
        embed = discord.Embed(
            description=f'Votes **enabled** in {channel.mention}!',
            colour=0x23b40c
        )
        await ctx.send(embed=embed)

    @votes.command()
    async def stop(self, ctx, channel: discord.TextChannel = None):
        if not await self.has_permissions(ctx):
            return
        channel = ctx.channel if channel is None else channel
        db.session.query(db.vote_channels).filter_by(server_id=ctx.guild.id).filter_by(channel_id=channel.id).delete()
        db.session.commit()
        if channel.id in self.vote_channels:
            index = np.argwhere(self.vote_channels==channel.id)
            self.vote_channels = np.delete(self.vote_channels, index)
        await ctx.message.delete()
        await ctx.channel.send(embed=discord.Embed(description=f'Votes has been stopped in {channel.mention}!', colour=0xf66045))

    async def has_permissions(self, ctx):
        if not ctx.channel.permissions_for(ctx.author).manage_channels and not await self.bot.is_owner(ctx.author):
            await ctx.send("You don't have permissions to do that", delete_after=10)
            return False
        return True

def setup(bot):
    bot.add_cog(Votes(bot))