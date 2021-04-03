import discord
from utils.store import store
import random
from discord.ext import commands
from pathlib import Path
from PIL import Image
import requests
import logging
from discord import File
import os

async def lineChooser(filename):
    lines = open(f'{store.resources_path}/{filename}').read().splitlines()
    return random.choice(lines)

class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def jack(self, ctx):
        await ctx.channel.send('"Fucking Jack!"')

    @commands.cooldown(6, 5)
    @commands.command()
    async def pp(self, ctx, member : discord.Member=None):
        member = ctx.author if member is None else member
        PP_Size = random.randint(3,20)
        if member.id == self.bot.owner_id:
            PP_Size = 20
        embed = discord.Embed(
            title = 'AYE DAWG NICE PEEPEE!',
            description = str(member.display_name) + '\'s pp size is ' + str(PP_Size) + 'cm 😘\n8' + ("=" * PP_Size) + 'D',
            colour = discord.Colour.magenta()
        )
        await ctx.channel.send(embed=embed)

    @commands.cooldown(6, 5)
    @commands.command(brief='Wanna hit on someone? Let me be your wingman!')
    async def pickup(self, ctx, member : discord.Member=None):
        member = ctx.author if member is None else member
        author = self.bot.user if member is ctx.author else ctx.author
        embed = discord.Embed(
            title = 'BOT PICKUPS! 🌈',
            description = str(author.display_name) + ' says: ay ' + str(member.display_name) + ', ' + await lineChooser("pickup.txt"),
            colour = discord.Colour.orange()
        )
        await ctx.channel.send(embed=embed)

    @commands.cooldown(6, 5)
    @commands.command(aliases=['insult','burn'], brief='Insult someone until they cry')
    async def roast(self, ctx, member : discord.Member=None):
        member = ctx.author if member is None else member
        author = self.bot.user if member is ctx.author else ctx.author
        if self.bot.user.id == member.id:
            replys = ['Simmer down buddy 🔫',
                    'You dare challenge thy master?! 💪',
                    'OK homie relax.. 💩',
                    'You aint even worth it dawg 🤏',
                    'HA! Good one. 😂',
                    'You done yet? Pussy.',
                    'Fuck off!!'
            ]
            await ctx.channel.send(random.choice(replys))
        else:
            embed = discord.Embed(
                title = 'BOT INSULTS! 🔥',
                description = str(author.display_name) + ' says: ay ' + str(member.display_name) + ', ' + await lineChooser("insults.txt"),
                colour = discord.Colour.orange()
            )
            await ctx.channel.send(embed=embed)

    @commands.cooldown(6, 5)
    @commands.command(aliases=['8ball'], brief='AKA 8ball, Ask the bot a question that you dont want the answer to.')
    async def eightball(self, ctx,*,question):
        responses = ['It is certain.',
                    'It is decidedly so.',
                    'Without a doubt.',
                    'Yes - definitely.',
                    'You may rely on it.',
                    'As I see it, yes.',
                    'Most likely.',
                    'Outlook good.',
                    'Yes.',
                    'Signs point to yes.',
                    'Reply hazy, try again.',
                    'Ask again later.',
                    'Better not tell you now.',
                    'Cannot predict now.',
                    'Concentrate and ask again.',
                    "Don't count on it.",
                    'My reply is no.',
                    'My sources say no.',
                    'Outlook not so good.',
                    'Very doubtful.']
        embed = discord.Embed(
            title=random.choice(responses),
            description=f'Question: {question}',
            colour = discord.Colour.orange()
        )
        embed.set_footer(text=f'Question by {ctx.author}', icon_url=ctx.author.avatar_url)
        await ctx.channel.send(embed=embed)


    @commands.command()
    async def secretDraw(self, ctx, offsetX: int, offsetY: int, resizeX: int = None, resizeY: int = None):
        if ctx.message.author.id == self.bot.owner_id:
            imageToDraw = Image.open(requests.get(ctx.message.attachments[0].url, stream=True).raw)
            if imageToDraw is not None:
                if resizeX and resizeY:
                    imageToDraw = imageToDraw.resize((resizeX,resizeY))
                width, height = imageToDraw.size
                pix = list(imageToDraw.getdata())

                fileTxt = open('pixelart.txt','w')
                im = Image.new('RGB', (1000,1000))
                for x in range(width):
                    badImage = False
                    for y in range(height):
                        index = x+y*width
                        if imageToDraw.mode in ('RGB'):
                            im.putpixel((x+offsetX, y+offsetY), pix[index])
                            hexColor = '#%02x%02x%02x' % pix[index]
                            fileTxt.write(f".place setpixel {x+offsetX} {y+offsetY} {hexColor}\n")
                        elif imageToDraw.mode in ('RGBA'):
                            if pix[index] != (0,0,0,0):
                                im.putpixel((x+offsetX, y+offsetY), pix[x+y*width])
                            hexColor = '#%02x%02x%02x%02x' % pix[index]
                            if hexColor != '#00000000':
                                fileTxt.write(f".place setpixel {x+offsetX} {y+offsetY} {hexColor}\n")
                        elif imageToDraw.mode in ('L'):
                            im.putpixel((x+offsetX, y+offsetY), (pix[index], pix[index], pix[index]))
                            hexColor = f'#{pix[index]:02x}{pix[index]:02x}{pix[index]:02x}'
                            fileTxt.write(f".place setpixel {x+offsetX} {y+offsetY} {hexColor}\n")
                        else:
                            await ctx.send(f'image has wrong color mode. cancelling')
                            badImage = True
                            break
                    if badImage:
                        break

                im.save("test2.png")
                if not badImage:
                    if os.stat('test2.png').st_size <= 8000000:
                        await ctx.send(file=File(Image.open('test2.png').filename))
                        if os.stat(fileTxt.name).st_size <= 8000000:
                             await ctx.send(file=File(fileTxt.name))
                    else:
                        await ctx.send('file too big')
                fileTxt.close()
            else:
                await ctx.send('No image to draw')

    @commands.command()
    async def spamDraw(self, ctx, offsetX: int, offsetY: int, resizeX: int = None, resizeY: int = None):
        if ctx.message.author.id == self.bot.owner_id:
            server = self.bot.get_guild(747752542741725244)
            channelToSpam = server.get_channel(819966095070330950)
            imageToDraw = Image.open(requests.get(ctx.message.attachments[0].url, stream=True).raw)
            if imageToDraw is not None:
                if resizeX and resizeY:
                    imageToDraw = imageToDraw.resize((resizeX,resizeY))
                width, height = imageToDraw.size
                pix = list(imageToDraw.getdata())
                for x in range(width):
                    badImage = False
                    for y in range(height):
                        index = x+y*width
                        if imageToDraw.mode in ('RGB'):
                            hexColor = '#%02x%02x%02x' % pix[index]
                            await channelToSpam.send(f".place setpixel {x+offsetX} {y+offsetY} {hexColor}\n")
                        elif imageToDraw.mode in ('RGBA'):
                            hexColor = '#%02x%02x%02x%02x' % pix[index]
                            if hexColor != '#00000000':
                                await channelToSpam.send(f".place setpixel {x+offsetX} {y+offsetY} {hexColor}\n")
                        elif imageToDraw.mode in ('L'):
                            hexColor = f'#{pix[index]:02x}{pix[index]:02x}{pix[index]:02x}'
                            await channelToSpam.send(f'.place setpixel {x+offsetX} {y+offsetY} {hexColor}')
                        else:
                            await channelToSpam.send(f'image has wrong color mode. cancelling')
                            badImage = True
                            break
                    if badImage:
                        break

    @commands.command()
    async def serversInfo(self, ctx):
        if ctx.message.author.id == self.bot.owner_id:
            serverList = []
            userList = []
            for guild in self.bot.guilds:
                serverList.append(f'{guild.name}::{guild.id}')
                userList.append(f'{guild.name} has {guild.member_count}')
            await ctx.send(f'{serverList}\n{userList}')

def setup(bot):
    bot.add_cog(Fun(bot))
