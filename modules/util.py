from pathlib import Path

import discord
import psutil
import subprocess
from colour import Color
from discord.ext import commands

Discord_Bot_Dir = Path("./")
linksPath = Path(Discord_Bot_Dir / "links/")
jackDiscordId = 276462585690193921
giveaway_channel = None


class Util(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

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

    @commands.command()
    async def sysinfo(self, ctx):
        if ctx.message.author.id == jackDiscordId:
            cpu_usage = psutil.cpu_percent()
            ram_total = psutil.virtual_memory().total >> 20
            ram_available = psutil.virtual_memory().available >> 20
            color_list = list(Color("green").range_to(Color("red"), 100))
            color = int("0x" + str(color_list[int(cpu_usage)].hex)[1:], 16)
            embed = discord.Embed(
                title="System usage information",
                colour=discord.Colour(color)
            )
            embed.add_field(name="CPU usage", value=f"{cpu_usage}%")
            embed.add_field(name="RAM usage", value=f"{ram_total - ram_available}/{ram_total}MB")
            await ctx.channel.send(embed=embed)

    @commands.command()
    async def run_command(self, ctx, *command):
        if ctx.message.author.id == jackDiscordId:
            output = ""
            try:
                output = subprocess.check_output(" ".join(command[:]), stderr=subprocess.STDOUT, shell=True).decode('utf-8')
            except subprocess.CalledProcessError:
                print(output)
            embed = discord.Embed(
                    title="Command output",
                    description=f"{output}",
                    colour = discord.Colour(0x1FE4FF)
                )
            await ctx.channel.send(embed=embed)


def setup(bot):
    bot.add_cog(Util(bot))
