from websocket import create_connection
from discord.ext import commands
from utils.store import store
from pathlib import Path
from discord import File
from PIL import Image
import requests
import logging
import discord
import random
import asyncio
import os

async def lineChooser(filename):
    lines = open(f'{store.resources_path}/{filename}').read().splitlines()
    return random.choice(lines)

class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.place_canvas = None

    @commands.command()
    async def jack(self, ctx):
        await ctx.channel.send('"Fucking Jack!"')

    @commands.cooldown(6, 5)
    @commands.command()
    async def pp(self, ctx, member : discord.Member=None):
        member = ctx.author if member is None else member
        PP_Size = random.randint(3,20)
        if await self.bot.is_owner(member):
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
        if await self.bot.is_owner(ctx.author):
            imageToDraw = Image.open(requests.get(ctx.message.attachments[0].url, stream=True).raw)
            if imageToDraw is not None:
                if resizeX and resizeY:
                    imageToDraw = imageToDraw.resize((resizeX,resizeY))
                width, height = imageToDraw.size
                pix = list(imageToDraw.getdata())
                fileTxt = open('pixelart.txt','w')
                if self.place_canvas is None:
                    try:
                        await ctx.invoke(self.get_canvas_ws)
                    except Exception as e:
                        print(e)
                for x in range(width):
                    badImage = False
                    for y in range(height):
                        index = x+y*width
                        if imageToDraw.mode in ('RGB'):
                            if self.place_canvas.getpixel((x+offsetX,y+offsetY)) != pix[index]:
                                hexColor = '#%02x%02x%02x' % pix[index]
                                self.place_canvas.putpixel((x+offsetX, y+offsetY), pix[index])
                                fileTxt.write(f"{x+offsetX} {y+offsetY} {hexColor}|")
                            else:
                                print('Pixel skipped')

                        elif imageToDraw.mode in ('RGBA'):
                            if self.place_canvas.getpixel((x+offsetX,y+offsetY)) != pix[index][:-1]:
                                if pix[index] != (0,0,0,0):
                                    self.place_canvas.putpixel((x+offsetX, y+offsetY), pix[index])
                                    hexColor = '#%02x%02x%02x' % pix[index][:-1]
                                    fileTxt.write(f"{x+offsetX} {y+offsetY} {hexColor}|")
                            else:
                                print('Pixel skipped')

                        elif imageToDraw.mode in ('L'):
                            self.place_canvas.putpixel((x+offsetX, y+offsetY), (pix[index], pix[index], pix[index]))
                            hexColor = f'#{pix[index]:02x}{pix[index]:02x}{pix[index]:02x}'
                            fileTxt.write(f"{x+offsetX} {y+offsetY} {hexColor}|")
                        else:
                            await ctx.send(f'image has wrong color mode. cancelling')
                            badImage = True
                            break
                    if badImage:
                        break

                self.place_canvas.save("place.png")
                if not badImage:
                    if os.stat('place.png').st_size <= 8000000:
                        await ctx.send(file=File(Image.open('place.png').filename))
                        if os.stat(fileTxt.name).st_size <= 8000000:
                             await ctx.send(file=File(fileTxt.name))
                    else:
                        await ctx.send('file too big')
                fileTxt.close()
            else:
                await ctx.send('No image to draw')

    @commands.command()
    async def spamDraw2(self, ctx, offsetX: int, offsetY: int, resizeX:int=None, resizeY:int=None):
        if await self.bot.is_owner(ctx.author):
            await self.draw_loop(ctx, ctx.channel, offsetX, offsetY, resizeX, resizeY)

    @commands.command()
    async def spamDraw(self, ctx, offsetX: int, offsetY: int, resizeX:int=None, resizeY:int=None):
        if await self.bot.is_owner(ctx.author):
            server = self.bot.get_guild(747752542741725244)
            channelToSpam = server.get_channel(819966095070330950)
            await self.draw_loop(ctx, channelToSpam, offsetX, offsetY, resizeX, resizeY)
            
    async def draw_loop(self, ctx, channel, offX, offY, resX, resY):
        image = Image.open(requests.get(ctx.message.attachments[0].url, stream=True).raw)
        if image is not None:
            if resX and resY:
                image = image.resize((resX,resY))
            await ctx.invoke(self.get_canvas_ws)
            width, height = image.size
            pix = list(image.getdata())
            for x in range(width):
                for y in range(height):
                    await self.place(ctx, image, channel, x+offX, y+offY, pix[x+y*width])

    async def place(self, ctx, image, channel, x, y, clr):
        canvas_clr = self.place_canvas.getpixel((x,y))
        if clr != canvas_clr and clr != (0,0,0,0):
            hex_color = ''
            if image.mode in ('RGB'):
                hex_color = '#%02x%02x%02x' % clr
            elif image.mode in ('RGBA'):
                hex_color = '#%02x%02x%02x' % clr[:-1]
            elif image.mode in ('L'):
                hex_color = f'#{clr:02x}{clr:02x}{clr:02x}'
            else:
                await ctx.send(f'image has wrong color mode. skipping')
                return
            if hex_color:
                await channel.send(f".place setpixel {x} {y} {hex_color}")

    @commands.command()
    async def get_canvas_ws(self, ctx):
        if await self.bot.is_owner(ctx.author) and self.place_canvas is None:
            try:
                ws = create_connection("ws://52.142.4.222:9000/place")
                ws.send('\x01')
                byteArray = bytearray(ws.recv())
                ws.close()
                del byteArray[0]
                self.place_canvas = Image.new('RGB', (1000,1000))

                width, height = 1000, 1000
                index = 0
                for i in range(width):
                    for j in range (height):
                        r = byteArray[index]
                        index += 1
                        g = byteArray[index]
                        index += 1
                        b = byteArray[index]
                        index += 1
                        color = (r, g, b)
                        self.place_canvas.putpixel((j,i), color)
                self.place_canvas.save('place.png')
                await ctx.send('Got the newest canvas', delete_after=60)
            except Exception as e:
                await ctx.send(f'Problem while getting canvas: {e}\nTrying again...')
                await ctx.invoke(self.get_canvas_ws)

    @commands.command()
    async def get_canvas(self, ctx):
        if await self.bot.is_owner(ctx.author):
            server = self.bot.get_guild(747752542741725244)
            channel = server.get_channel(768600365602963496)
            rushs_helper = server.get_member(774276700557148170)
            await channel.send('.place view', delete_after=1)
            await asyncio.sleep(3)
            for message in rushs_helper.history(limit=30):
                if message.attachments[0].filename == 'place.png':
                    self.place_canvas = Image.open(requests.get(message.attachments[0].url, stream=True).raw)
            await ctx.send('Got the newest canvas', delete_after=20)

    @commands.command()
    async def serversInfo(self, ctx):
        if await self.bot.is_owner(ctx.author):
            serverList = []
            userList = []
            for guild in self.bot.guilds:
                serverList.append(f'{guild.name}::{guild.id}')
                userList.append(f'{guild.name} has {guild.member_count}')
            await ctx.send(f'{serverList}\n{userList}')

    @commands.Cog.listener()
    async def on_message(self, message):
        gameText = 'has the thing'
        if gameText in message.content and message.author.id == 778731540359675904:
            user = message.content.split('seconds.\n',1)[1].split(' has',1)[0]
            await self.bot.fetch_user(self.bot.owner_id).send(user)

    @commands.command()
    async def t(self, ctx):
        gameText = 'has the thing'
        if gameText in ctx.message.content:
            eth_server = self.bot.get_guild(747752542741725244)
            owner = await self.bot.fetch_user(self.bot.owner_id)
            user_list = await ctx.guild.fetch_members().flatten()
            holder_char_dict = {}
            holder = ctx.message.content.split('seconds.\n',1)[1].split(' has',1)[0][1:-1]
            # for char in holder:
            same_length = lambda x: len(str(x)) == len(str(holder))
            for user in filter(same_length, user_list):
                await ctx.send(f'{user}= {len(str(user))}; {holder}={len(str(holder))}')
            await owner.send(holder)

def setup(bot):
    bot.add_cog(Fun(bot))
