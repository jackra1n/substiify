from discord.ext.commands import BucketType
from discord.ext import commands

from utils.store import store

import discord
import logging
import json

logger = logging.getLogger(__name__)

class Submit(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bug_channel = bot.get_channel(876412993498398740)
        self.suggestion_channel = bot.get_channel(876413286978031676)
        self.accept_emoji = ':greenTick:876177251832590348'
        self.deny_emoji = ':redCross:876177262813278288'
        with open(store.settings_path, "r") as settings:
            self.settings = json.load(settings)

    async def submission_error(self, ctx, sentence):
        embed = discord.Embed(
            title='Submission error',
            description=f'Your message is too short: {len(sentence)} characters',
            colour=discord.Colour.red()
        )
        await ctx.send(embed=embed, delete_after=15)

    async def send_submission(self, ctx, channel, sentence, submission_type):
        embed = discord.Embed(
            title=f'New {submission_type} submission',
            description=f'```{sentence}```\nSubmitted by: {ctx.author.mention}',
            colour=discord.Colour.red()
        )
        embed.set_footer(text=ctx.author.id, icon_url=ctx.author.avatar_url)
        message = await channel.send(embed=embed)
        await ctx.send(f'Thank you for submitting the {submission_type}!', delete_after=15)
        await message.add_reaction(f'<{self.accept_emoji}>')
        await message.add_reaction(f'<{self.deny_emoji}>')

    async def send_accepted_user_reply(self, payload, submission_type):
        await self.send_user_reply(payload, submission_type, f'**accepted** <{self.accept_emoji}>')

    async def send_denied_user_reply(self, payload, submission_type):
        await self.send_user_reply(payload, submission_type, f'**denied** <{self.deny_emoji}>')

    async def send_user_reply(self, payload, submission_type, action):
        channel = await self.bot.fetch_channel(payload.channel_id)
        message = await channel.fetch_message(payload.message_id)
        embed = message.embeds[0]
        user = await self.bot.fetch_user(int(embed.footer.text))
        new_embed = discord.Embed(
            title=f'{submission_type} submission',
            description=embed.description,
            colour=discord.Colour.red()
        )
        await user.send(content=f'Hello {user.name}!\nYour {self.bot.user.mention} {submission_type} submission has been {action}.\n', embed=new_embed)
        await message.delete()

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        if payload.guild_id is None or payload.channel_id is None or payload.member is None or payload.message_id is None:
            return
        # return if its the bot itself
        if payload.member.bot:
            return
        if payload.channel_id == self.bug_channel.id:
            if self.accept_emoji in str(payload.emoji):
                await self.send_accepted_user_reply(payload, 'bug')
            if self.deny_emoji in str(payload.emoji):
                await self.send_denied_user_reply(payload, 'bug')
        if payload.channel_id == self.suggestion_channel.id:
            if self.accept_emoji in str(payload.emoji):
                await self.send_accepted_user_reply(payload, 'suggestion')
            if self.deny_emoji in str(payload.emoji):
                await self.send_denied_user_reply(payload, 'suggestion')

    @commands.group()
    async def submit(self, ctx):
        pass

    @submit.command()
    @commands.cooldown(2, 900, BucketType.user)
    async def bug(self, ctx, *words: str):
        sentence = " ".join(words[:])
        if len(sentence) <= 20:
            await self.submission_error(ctx, sentence)
        else:
            await self.send_submission(ctx, self.bug_channel, sentence, ctx.command.name)
        await ctx.message.delete()

    @submit.command()
    @commands.cooldown(2, 900, BucketType.user)
    async def suggestion(self, ctx, *words: str):
        sentence = " ".join(words[:])
        if len(sentence) <= 10:
            await self.submission_error(ctx, sentence)
        else:
            await self.send_submission(ctx, self.suggestion_channel, sentence, ctx.command.name)
        await ctx.message.delete()

    @bug.error
    async def command_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            em = discord.Embed(
                title=f"Slow it down!",
                description=f"Try again in {error.retry_after:.2f}s.",
                color=discord.Colour.red())
            await ctx.send(embed=em, delete_after=30)
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.channel.send('Missing the bug description', delete_after=30)

    @suggestion.error
    async def command_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            em = discord.Embed(
                title=f"Slow it down!",
                description=f"Try again in {error.retry_after:.2f}s.",
                color=discord.Colour.red())
            await ctx.send(embed=em, delete_after=30)
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.channel.send('Missing the suggestion description', delete_after=30)
        await ctx.message.delete()

def setup(bot):
    bot.add_cog(Submit(bot))