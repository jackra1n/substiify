from helper.ModulesManager import ModulesManager
from utils.store import store
from discord.ext import commands
from datetime import datetime
from pytz import timezone
from enum import Enum

import subprocess
import platform
import discord
import logging
import psutil
import json

logger = logging.getLogger(__name__)

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

class Util(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        with open(store.settings_path, "r") as settings:
            self.settings = json.load(settings)

    @commands.cooldown(6, 5)
    @commands.command(aliases=['avatar'],brief='Enlarge and view your profile picture or another member')
    async def av(self, ctx, member: discord.Member = None):
        member = ctx.author if member is None else member
        embed = discord.Embed(
            title=str(member.display_name),
            description='Avatar',
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
        message = await ctx.fetch_message(message_id)
        await message.delete()
        await ctx.message.delete()

    @clear.error
    async def clear_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.channel.send('Please put an amount to clear.')

    @commands.command(aliases=['dink'])
    async def ping(self, ctx):
        title = 'Pong!'
        if 'dink' in ctx.message.content.lower():
            title = 'Donk!'
        embed = discord.Embed(title=f'{title} 🏓', description=f'⏱️Ping:')
        start = datetime.now()
        ping = await ctx.send(embed=embed)
        end = datetime.now()
        embed = discord.Embed(title=f'{title} 🏓', description=f'⏱️Ping:`{round((end - start).microseconds / 1000)}` ms')
        await ping.edit(embed=embed)

    @commands.command()
    async def specialThanks(self, ctx):
        embed = discord.Embed(
            title="Special thanks for any help to those people",
            description = f'<@205704051856244736> <@812414532563501077> <@299478604809764876> <@291291715598286848> <@224618877626089483> <@231151428167663616>'
        )
        await ctx.channel.send(embed=embed)

    @commands.command()
    async def info(self, ctx):
        bot_time = time_up((datetime.now() - store.script_start).total_seconds()) #uptime of the bot
        cpu_usage = psutil.cpu_percent()
        ram_usage = psutil.virtual_memory().percent
        with open(store.settings_path, "r") as settings:
            self.settings = json.load(settings)

        content = f'**Instance uptime:** `{bot_time}`\n' \
            f'**Version:** `{self.settings["version"]}`\n' \
            f'**Python:** `{platform.python_version()}` | **discord.py:** `{discord.__version__}`\n\n' \
            f'**CPU:** `{cpu_usage}%` | **RAM:** `{ram_usage}%`\n\n' \
            f'**Made by:** <@{self.bot.owner_id}>\n' \
            f'**Source:** No link yet' 

        embed = discord.Embed(
            title=f'Info about {self.bot.user.display_name}',
            description=content, colour=discord.Colour(0xc44c27),
            timestamp=datetime.now(timezone("Europe/Zurich"))
        )
        embed.set_thumbnail(url=self.bot.user.avatar_url)
        embed.set_footer(text=f"Requested by by {ctx.author.display_name}")
        await ctx.channel.send(embed=embed)

    @commands.command()
    @commands.is_owner()
    async def setversion(self, ctx, version):
        with open(store.settings_path, "r") as settings:
            settings_json = json.load(settings)
        settings_json['version'] = version
        with open(store.settings_path, "w") as settings:
            json.dump(settings_json, settings, indent=2)
        if ctx.channel.permissions_for(ctx.guild.me).manage_messages:
            await ctx.message.delete()
        embed = discord.Embed(description=f'Version has been set to {version}')
        await ctx.send(embed=embed, delete_after=10)

    @commands.group()
    async def module(self, ctx):
        pass

    @module.command()
    @commands.guild_only()
    async def toggle(self, ctx, module):
        if not await has_permissions_to_manage(ctx):
            return
        if module in ModulesManager.get_commands():
            result = ModulesManager.toggle_module(ctx.guild.id, module)
            await ctx.send(f'Module `{module}` has been **{result}**', delete_after=10)
        else:
            await ctx.send(f'Module \'{module}\' not found', delete_after=10)

    @toggle.error
    async def command_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.channel.send('Argument required:')

    @module.command()
    async def list(self, ctx):
        if not await has_permissions_to_manage(ctx):
            return
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
        await ctx.send(embed=embed, delete_after=180)

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