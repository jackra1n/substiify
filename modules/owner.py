from discord import Activity, ActivityType
from discord.ext import commands, tasks

from utils.store import store
from utils import util
from os import walk, path

import discord
import subprocess
import logging
import json

logger = logging.getLogger(__name__)

reload_capable_users = [276462585690193921, 307685227751276545, 510183286547546132, 464861706665984010]

class Owner(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.status_task.start()
        self.prefix = util.prefixById(self.bot)
        with open(store.settings_path, "r") as settings:
            self.settings = json.load(settings)

    async def set_default_status(self):
        servers = len(self.bot.guilds)
        self.prefix = util.prefixById(self.bot)
        activityName = f"{self.prefix}help | {servers} servers"
        activity = Activity(type=ActivityType.listening, name=activityName)
        await self.bot.change_presence(activity=activity)

    @tasks.loop(minutes=30)
    async def status_task(self):
        await self.set_default_status()

    @commands.command()
    async def shutdown(self, ctx):
        if ctx.author.id == 276462585690193921 or ctx.author.id == 205704051856244736:
            embed = discord.Embed(description=f'Shutting down...', colour=0xf66045)
            await ctx.send(embed=embed)
            await self.bot.close()

    @commands.command()
    async def reload(self, ctx):
        if ctx.author.id in reload_capable_users:
            await ctx.message.add_reaction('<:greenTick:876177251832590348>')
            self.bot.get_cog('Daydeal').daydeal_task.stop()
            subprocess.run(["/bin/git","pull","--no-edit"])
            try:
                for cog in self.get_modules():
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
        self.status_task.stop()
        activityName = f"{self.prefix}help | {count} servers"
        activity = Activity(type=ActivityType.listening, name=activityName)
        await self.bot.change_presence(activity=activity)

    @status.command()
    @commands.is_owner()
    async def set(self, ctx, *text: str):
        self.status_task.stop()
        status = " ".join(text[:])
        activity = Activity(type=ActivityType.listening, name=status)
        await self.bot.change_presence(activity=activity)

    @status.command()
    @commands.is_owner()
    async def reset(self, ctx):
        await self.set_default_status()
        self.status_task.restart()

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

    @commands.is_owner()
    @commands.command()
    async def checkVCs(self, ctx, server_id : int):
        if server_id is None:
            return await ctx.send("Please provide a server ID to be checked", delete_after = 5)
        await ctx.send(f"trying to get server with id `{server_id}`...", delete_after = 5)
        server = self.bot.get_guild(server_id)
        await ctx.send(f"server is {server.name}", delete_after = 5)
        if len(server.voice_channels) == 0:
            return await ctx.send(f"No voice channels on {server.name}", delete_after = 20)
        for vc in server.voice_channels:
            if len(vc.members) > 0:
                members = ""
                for member in vc.members:
                    members += f"{member.display_name}\n"
                embed = discord.Embed(
                    title = vc.name,
                    description = members,
                    colour = discord.Colour.blurple()
                )
                await ctx.send(embed=embed)
        await ctx.message.delete()

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

    def get_modules(self):
        filenames = next(walk("modules"), (None, None, []))[2] 
        filenames.remove(path.basename(__file__))
        return [name.replace('.py','') for name in filenames]

def setup(bot):
    bot.add_cog(Owner(bot))