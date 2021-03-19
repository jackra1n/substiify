from pathlib import Path
import discord
import psutil
import subprocess
import time
from colour import Color
from discord.ext import commands

Discord_Bot_Dir = Path("./")
linksPath = Path(Discord_Bot_Dir / "links/")

class Util(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.script_start = time.time()

    @commands.cooldown(6, 5)
    @commands.command(brief='Enlarge and view your profile picture or another member')
    async def av(self, ctx, member: discord.Member = None):
        member = ctx.author if member is None else member
        embed = discord.Embed(
            title=str(member.name),
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
        start = time.perf_counter()
        ping = await ctx.send(embed=embed)
        end = time.perf_counter()
        embed = discord.Embed(title=f'{title} 🏓', description=f'⏱️Ping:`{round((end - start) * 1000)}` ms')
        await ping.edit(embed=embed)

    @commands.command()
    async def sysinfo(self, ctx):
        if ctx.message.author.id == self.bot.owner_id:
            bot_time = time_up(time.time() - self.script_start) #uptime of the bot
            cpu_usage = psutil.cpu_percent()
            ram_total = psutil.virtual_memory().total >> 20
            ram_available = psutil.virtual_memory().available >> 20
            color_list = list(Color("green").range_to(Color("red"), 100))
            color = int("0x" + str(color_list[int(cpu_usage)].hex)[1:], 16)
            embed = discord.Embed(
                title="System usage information",
                colour=discord.Colour(color),
                description = f'**Instance uptime:** `{bot_time}`'
            )
            embed.add_field(name="CPU usage", value=f"{cpu_usage}%")
            embed.add_field(name="RAM usage", value=f"{ram_total - ram_available}/{ram_total}MB")
            await ctx.channel.send(embed=embed)

    @commands.command()
    async def specialThanks(self, ctx):
        embed = discord.Embed(
            title="Special thanks for any help to those people",
            description = f'<@205704051856244736> <@812414532563501077> <@299478604809764876> <@291291715598286848>'
        )
        await ctx.channel.send(embed=embed)

    @commands.command()
    async def run_command(self, ctx, *command):
        if ctx.message.author.id == self.bot.owner_id:
            output = ""
            try:
                output = subprocess.check_output(" ".join(command[:]), stderr=subprocess.STDOUT, shell=True).decode('utf-8')
                embed = discord.Embed(
                        title="Command output",
                        description=f"{output}",
                        colour = discord.Colour(0x1FE4FF)
                    )
                await ctx.channel.send(embed=embed)
            except subprocess.CalledProcessError:
                print(output)
                await ctx.channel.send(output)

def setup(bot):
    bot.add_cog(Util(bot))


def time_up(t):
    if t <= 60:
        return f"{int(t)} seconds"
    elif 3600 > t > 60:
        minutes = t // 60
        seconds = t % 60
        return f"{int(minutes)} minutes and {int(seconds)} seconds"
    elif t >= 3600:
        hours = t // 3600  # Seconds divided by 3600 gives amount of hours
        minutes = (t % 3600) // 60  # The remaining seconds are looked at to see how many minutes they make up
        seconds = (t % 3600) - minutes * 60  # Amount of minutes remaining minus the seconds the minutes "take up"
        if hours >= 24:
            days = hours // 24
            hours = hours % 24
            return f"{int(days)} days, {int(hours)} hours, {int(minutes)} minutes and {int(seconds)} seconds"
        else:
            return f"{int(hours)} hours, {int(minutes)} minutes and {int(seconds)} seconds"