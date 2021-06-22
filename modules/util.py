from utils.store import store
from discord.ext import commands
from datetime import datetime
from pytz import timezone
import subprocess
import platform
import discord
import logging
import psutil
import json
from discordTogether import DiscordTogether

logger = logging.getLogger(__name__)

class Util(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.togetherControl = DiscordTogether(self.bot)
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

    @commands.command(brief='Clears messages within the current channel.')
    @commands.has_permissions(manage_messages=True)
    async def clear(self, ctx, amount):
        amount = int(amount)
        if amount <= 100:
            await ctx.channel.purge(limit=amount + 1)
        else:
            await ctx.channel.send('Cannot delete more than 100 messages at a time!')

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
    async def run_command(self, ctx, *command):
        if ctx.message.author.id == self.bot.owner_id:
            output = subprocess.check_output(" ".join(command[:]), stderr=subprocess.STDOUT, shell=True).decode('utf-8')
            embed = discord.Embed(
                    title="Command output",
                    description=f"{output}",
                    colour = discord.Colour(0x1FE4FF)
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
    async def setversion(self, ctx, version):
        if ctx.message.author.id == self.bot.owner_id:
            with open(store.settings_path, "r") as settings:
                settings_json = json.load(settings)
            settings_json['version'] = version
            with open(store.settings_path, "w") as settings:
                json.dump(settings_json, settings, indent=2)
            if ctx.channel.permissions_for(ctx.guild.me).manage_messages:
                await ctx.message.delete()
            embed = discord.Embed(description=f'Version has been set to {version}')
            await ctx.send(embed=embed, delete_after=10)

    @commands.command()
    async def createRoom(self, ctx, room):
        link = await self.togetherControl.create_link(ctx.author.voice.channel.id, room)
        await ctx.send(f'Click the blue link!\n{link}')

    @commands.command()
    async def possibleRooms(self, ctx):
        await ctx.send(f'youtube, poker, betrayal, fishing, chess')

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
        else:
            return f"{int(hours)} hours, {int(minutes)} minutes"