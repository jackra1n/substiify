import discord
import random
from discord.ext import commands
from pathlib import Path

Discord_Bot_Dir = Path("./")
linksPath = Path(Discord_Bot_Dir / "resources/")


async def lineChooser(filename):
    lines = open(linksPath / filename).read().splitlines()
    return random.choice(lines)


async def embedSender(self, ctx, member, text, file):
    member = ctx.author if member is None else member
    author = self.bot.user if member is ctx.author else ctx.author
    embed = discord.Embed(
        title=author.display_name + text + member.display_name,
        colour=discord.Colour.from_rgb(0, 0, 0)
    )
    embed.set_image(url=await lineChooser(file))
    await ctx.channel.send(embed=embed)


class Gif(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(brief='Hug someone or yourself')
    async def hug(self, ctx, member: discord.Member = None):
        await embedSender(self, ctx, member, " hugs ", "hug.txt")

    @commands.command(brief='Bite someone or yourself')
    async def bite(self, ctx, member: discord.Member = None):
        await embedSender(self, ctx, member, " bites ", "bite.txt")

    @commands.command(brief='Cuddle someone or yourself')
    async def cuddle(self, ctx, member: discord.Member = None):
        await embedSender(self, ctx, member, " cuddles ", "cuddle.txt")

    @commands.command(brief='Kiss someone or yourself')
    async def kiss(self, ctx, member: discord.Member = None):
        await embedSender(self, ctx, member, " kisses ", "kiss.txt")

    @commands.command(brief='Slap someone or yourself')
    async def slap(self, ctx, member: discord.Member = None):
        await embedSender(self, ctx, member, " slaps ", "slap.txt")


def setup(bot):
    bot.add_cog(Gif(bot))
