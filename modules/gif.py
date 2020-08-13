import discord
import random
from discord.ext import commands
from pathlib import Path

Discord_Bot_Dir = Path("./")
linksPath = Path(Discord_Bot_Dir/"links/")

async def lineChooser(filename):
    lines = open(linksPath / filename).read().splitlines()
    return random.choice(lines)

class Gif(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(brief='Hug someone or yourself')
    async def hug(self, ctx, member : discord.Member=None):
        member = ctx.author if member is None else member
        author = self.bot.user if member is ctx.author else ctx.author
        embed = discord.Embed(
            title = author.name + ' hugs ' + member.name + ' 🤗',
            colour = discord.Colour.from_rgb(0,0,0)
        )
        embed.set_image(url=await lineChooser("hug.txt"))
        await ctx.channel.send(embed=embed)
        file.close()

    @commands.command(brief='Bite someone or yourself')
    async def bite(self, ctx, member : discord.Member=None):
        member = ctx.author if member is None else member
        author = self.bot.user if member is ctx.author else ctx.author
        embed = discord.Embed(
            title = str(author.name) + ' bites ' + str(member.name),
            colour = discord.Colour.from_rgb(0,0,0)
        )
        embed.set_image(url=await lineChooser("bite.txt"))
        await ctx.channel.send(embed=embed)
        file.close()
    
    @commands.command(brief='Cuddle someone or yourself')
    async def cuddle(self, ctx, member : discord.Member=None):
        member = ctx.author if member is None else member
        author = self.bot.user if member is ctx.author else ctx.author
        embed = discord.Embed(
            title = str(author.name) + ' cuddles ' + str(member.name) + ' 🤗',
            colour = discord.Colour.from_rgb(0,0,0)
        )
        embed.set_image(url=await lineChooser("cuddle.txt"))
        await ctx.channel.send(embed=embed)
        file.close()

    @commands.command(brief='Kiss someone or yourself')
    async def kiss(self, ctx, member : discord.Member=None):
        member = ctx.author if member is None else member
        author = self.bot.user if member is ctx.author else ctx.author
        embed = discord.Embed(
            title = str(author.name) + ' kisses ' + str(member.name) + ' 💋',
            colour = discord.Colour.from_rgb(0,0,0)
        )
        embed.set_image(url=await lineChooser("kiss.txt"))
        await ctx.channel.send(embed=embed)
        file.close()

    @commands.command(brief='Slap someone or yourself')
    async def slap(self, ctx, member : discord.Member=None):
        member = ctx.author if member is None else member
        author = self.bot.user if member is ctx.author else ctx.author
        embed = discord.Embed(
            title = str(author.name) + ' slaps ' + str(member.name) + ' 😡',
            colour = discord.Colour.from_rgb(0,0,0)
        )
        embed.set_image(url=await lineChooser("slap.txt"))
        await ctx.channel.send(embed=embed)
        file.close()

def setup(bot):
    bot.add_cog(Gif(bot))