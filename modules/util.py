from random import shuffle
from helper.ModulesManager import ModulesManager
from utils.store import store
from discord.ext import commands
from datetime import datetime
from pytz import timezone

import platform
import discord
import logging
import psutil
import json

logger = logging.getLogger(__name__)

class Util(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        with open(store.settings_path, "r") as settings:
            self.settings = json.load(settings)

    @commands.cooldown(6, 5)
    @commands.command(aliases=['avatar'],brief='Enlarge and view your profile picture or another member')
    async def av(self, ctx, member: discord.Member = None):
        await ctx.message.delete()
        member = ctx.author if member is None else member
        embed = discord.Embed(
            title=f"{str(member.display_name)}'s avatar",
            url=member.avatar_url,
            colour=discord.Colour.light_grey()
        )
        embed.set_image(url=member.avatar_url)
        await ctx.channel.send(embed=embed)

    @commands.group(brief='Clears messages within the current channel.', invoke_without_command = True)
    async def clear(self, ctx, amount):
        if not await has_permissions_to_delete(ctx):
            return
        amount = int(amount)
        if amount <= 100:
            await ctx.channel.purge(limit=amount + 1)
        else:
            await ctx.channel.send('Cannot delete more than 100 messages at a time!')

    @clear.command()
    async def message(self, ctx, message_id: int):
        if not await has_permissions_to_delete(ctx):
            return
        await ctx.message.delete()
        message = await ctx.fetch_message(message_id)
        await message.delete()

    @clear.error
    async def clear_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.channel.send('Please put an amount to clear.')

    @commands.command(aliases=['dink'])
    async def ping(self, ctx):
        title = 'Pong!'
        if 'dink' in ctx.message.content.lower():
            title = 'Donk!'
        embed = discord.Embed(title=f'{title} 🏓', description=f'⏱️Ping:`{round(self.bot.latency*1000)}` ms')
        await ctx.message.delete()
        await ctx.send(embed=embed)

    @commands.command()
    async def specialThanks(self, ctx):
        peeople_who_helped = ["<@205704051856244736>", "<@812414532563501077>", "<@299478604809764876>", "<@291291715598286848>", "<@224618877626089483>", "<@231151428167663616>"]
        shuffle(peeople_who_helped)
        embed = discord.Embed(
            title="Special thanks for any help to those people",
            description = f" ".join(peeople_who_helped)
        )
        await ctx.message.delete()
        await ctx.channel.send(embed=embed, delete_after=120)

    @commands.command()
    async def info(self, ctx):
        await ctx.message.delete()
        bot_time = time_up((datetime.now() - store.script_start).total_seconds()) #uptime of the bot
        cpu_percent = psutil.cpu_percent()
        ram = psutil.virtual_memory()
        ram_used = format_bytes((ram.total - ram.available))
        ram_percent = psutil.virtual_memory().percent
        with open(store.settings_path, "r") as settings:
            self.settings = json.load(settings)

        content = f'**Instance uptime:** `{bot_time}`\n' \
            f'**Version:** `{self.settings["version"]}`\n' \
            f'**Python:** `{platform.python_version()}` | **discord.py:** `{discord.__version__}`\n\n' \
            f'**CPU:** `{cpu_percent}%` | **RAM:** `{ram_used} ({ram_percent}%)`\n\n' \
            f'**Made by:** <@{self.bot.owner_id}>\n' \
            f'**Source:** [Link](https://github.com/jackra1n/substiify)' 

        embed = discord.Embed(
            title=f'Info about {self.bot.user.display_name}',
            description=content, colour=discord.Colour(0xc44c27),
            timestamp=datetime.now(timezone("Europe/Zurich"))
        )
        embed.set_thumbnail(url=self.bot.user.avatar_url)
        embed.set_footer(text=f"Requested by by {ctx.author.display_name}")
        await ctx.channel.send(embed=embed)

    @commands.group()
    async def module(self, ctx):
        pass

    @module.command()
    @commands.guild_only()
    async def toggle(self, ctx, module):
        if not await has_permissions_to_manage(ctx):
            return
        await ctx.message.delete()
        if module in ModulesManager.get_commands():
            result = ModulesManager.toggle_module(ctx.guild.id, module)
            await ctx.send(f'Module `{module}` has been **{result}**')
        else:
            await ctx.send(f'Module \'{module}\' not found', delete_after=30)

    @toggle.error
    async def command_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.channel.send('Argument required:')

    @module.command(aliases=['list'])
    async def module_list(self, ctx):
        if not await has_permissions_to_manage(ctx):
            return
        await ctx.message.delete()
        commandStatuses = ''
        commandNames = ''
        for command in ModulesManager.get_commands():
            if ModulesManager._is_enabled(ctx.guild.id, command):
                commandStatuses += '`enabled ` <:greenTick:876177251832590348>\n'  
            else:
                commandStatuses += '`disabled` <:redCross:876177262813278288>\n'
            commandNames += f'{command}\n'
        embed = discord.Embed(
            title='Module List',
            colour=discord.Colour.blurple()
        )
        embed.add_field(name='Command', value=commandNames, inline=True)
        embed.add_field(name='Status', value=commandStatuses, inline=True)
        await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(Util(bot))

def time_up(t):
    if t <= 60:
        return f"<1 minute"
    elif 3600 > t > 60:
        minutes = t // 60
        return f"{int(minutes)} minutes"
    elif t >= 3600:
        hours = t // 3600  # Seconds divided by 3600 gives amount of hours
        minutes = (t % 3600) // 60  # The remaining seconds are looked at to see how many minutes they make up
        if hours >= 24:
            days = hours // 24
            hours = hours % 24
            return f"{int(days)} days, {int(hours)} hours, {int(minutes)} minutes"
        return f"{int(hours)} hours, {int(minutes)} minutes"

def format_bytes(size: int) -> str:
    # 2**10 = 1024
    power = 2**10
    n = 0
    power_labels = {0 : '', 1: 'KB', 2: 'MB', 3: 'GB', 4: 'TB'}
    while size > power:
        size /= power
        n += 1
    return f'{round(size, 2)}{power_labels[n]}'

async def has_permissions_to_delete(ctx):
    if not ctx.channel.permissions_for(ctx.author).manage_messages and not await ctx.bot.is_owner(ctx.author):
        await ctx.send("You don't have permissions to do that", delete_after=10)
        await ctx.message.delete()
        return False
    return True

async def has_permissions_to_manage(ctx):
    if not ctx.channel.permissions_for(ctx.author).manage_channels and not await ctx.bot.is_owner(ctx.author):
        await ctx.send("You don't have permissions to do that", delete_after=10)
        await ctx.message.delete()
        return False
    return True
