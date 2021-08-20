from os import stat
from discord import Activity, ActivityType
from utils.store import store
from discord.ext import commands
from utils import util

import discord
import subprocess
import logging
import json

logger = logging.getLogger(__name__)

class Owner(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.prefix = util.prefixById(self.bot)
        with open(store.settings_path, "r") as settings:
            self.settings = json.load(settings)

    @commands.command()
    @commands.is_owner()
    async def reload(self, ctx):
        await ctx.message.add_reaction('<:greenTick:876177251832590348>')
        self.bot.get_cog('Daydeal').daydeal_task.stop()
        subprocess.run(["/bin/git","pull","--no-edit"])
        try:
            for cog in self.startup_extensions:
                self.bot.reload_extension(f'modules.{cog}')
        except Exception as e:
            exc = f'{type(e).__name__}: {e}'
            await ctx.channel.send(f'Failed to reload extensions\n{exc}')
        await ctx.channel.send('Reloaded all cogs', delete_after=120)
        await ctx.message.delete()

    @commands.group()
    async def status(self, ctx):
        pass

    @status.command()
    @commands.is_owner()
    async def count(self, ctx, count):
        self.bot.get_cog('MainBot').status_task.stop()
        activityName = f"{self.prefix}help | {count} servers"
        activity = Activity(type=ActivityType.listening, name=activityName)
        await self.bot.change_presence(activity=activity)

    @status.command()
    @commands.is_owner()
    async def set(self, ctx, *text: str):
        self.bot.get_cog('MainBot').status_task.stop()
        status = " ".join(text[:])
        activity = Activity(type=ActivityType.listening, name=status)
        await self.bot.change_presence(activity=activity)

    @status.command()
    @commands.is_owner()
    async def reset(self, ctx):
        self.bot.get_cog('MainBot').status_task.restart()

    @commands.group()
    async def server(self, ctx):
        pass

    @commands.is_owner()
    @server.command(aliases=['list'])
    async def server_list(self, ctx):
        servers = ''
        user_count = ''
        server_ids = ''
        for guild in self.bot.guilds:
            servers += f'{guild.name}\n'
            user_count += f'{guild.member_count}\n'
            server_ids += f'{guild.id}\n'
        embed = discord.Embed(
            title='Server Infos',
            colour=discord.Colour.blurple()
        )
        embed.add_field(name='Name', value=servers, inline=True)
        embed.add_field(name='User count', value=user_count, inline=True)
        embed.add_field(name='Id', value=server_ids, inline=True)
        await ctx.send(embed=embed, delete_after=60)

    @commands.command()
    @commands.is_owner()
    async def version(self, ctx, version):
        with open(store.settings_path, "r") as settings:
            settings_json = json.load(settings)
        settings_json['version'] = version
        with open(store.settings_path, "w") as settings:
            json.dump(settings_json, settings, indent=2)
        if ctx.channel.permissions_for(ctx.guild.me).manage_messages:
            await ctx.message.delete()
        embed = discord.Embed(description=f'Version has been set to {version}')
        await ctx.send(embed=embed, delete_after=10)

def setup(bot):
    bot.add_cog(Owner(bot))