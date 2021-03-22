import discord
from utils.store import store
import random
from discord.ext import commands
from pathlib import Path
from PIL import Image
import requests
from discord import File

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
    async def secretDraw(self, ctx, offsetX, offsetY):
        if ctx.message.author.id == self.bot.owner_id:
            channel_to_spam = 819966095070330950
            imageToDraw = Image.open(requests.get(ctx.message.attachments[0].url, stream=True).raw)
            if imageToDraw is not None:
                width, height = imageToDraw.size
                pix_val = list(imageToDraw.getdata())

                fileTxt = open('pixelart.txt','w')
                im = Image.new('RGB', (1000,1000))

                i = 0
                for x in range(width):
                    for y in range(height):
                        if imageToDraw.mode in ('RGB'):
                            im.putpixel((y+int(offsetX),x+int(offsetY)), pix_val[i])
                            fileTxt.write(f".place setpixel {y+int(offsetX)} {x+int(offsetY)} " + '#%02x%02x%02x' % pix_val[i]+"\n")
                        elif imageToDraw.mode in ('L'):
                            im.putpixel((y+int(offsetX),x+int(offsetY)), (pix_val[i], pix_val[i], pix_val[i]))
                            fileTxt.write(f".place setpixel {y+int(offsetX)} {x+int(offsetY)} " + f'#{pix_val[i]:02x}{pix_val[i]:02x}{pix_val[i]:02x}'+"\n")
                        else:
                            await channelToSpam.send(f'image has wrong color mode. cancelling')
                            break
                        i += 1

                im.save("test2.png")
            await ctx.channel.send(file=File(fileTxt.name))
            await ctx.channel.send(file=File(Image.open('test2.png').filename))
            fileTxt.close()

    @commands.command()
    async def spamDraw(self, ctx, offsetX, offsetY):
        if ctx.message.author.id == self.bot.owner_id:
            server = self.bot.get_guild(747752542741725244)
            channelToSpam = server.get_channel(819966095070330950)
            imageToDraw = Image.open(requests.get(ctx.message.attachments[0].url, stream=True).raw)
            if imageToDraw is not None:
                width, height = imageToDraw.size
                pix_val = list(imageToDraw.getdata())
                i = 0
                for x in range(width):
                    for y in range(height):
                        if imageToDraw.mode in ('RGB'):
                            await channelToSpam.send(f".place setpixel {y+int(offsetX)} {x+int(offsetY)} " + '#%02x%02x%02x' % pix_val[i]+"\n")
                        elif imageToDraw.mode in ('L'):
                            await channelToSpam.send(f".place setpixel {y+int(offsetX)} {x+int(offsetY)} " + f'#{pix_val[i]:02x}{pix_val[i]:02x}{pix_val[i]:02x}')
                        else:
                            await channelToSpam.send(f'image has wrong color mode. cancelling')
                            break
                        i += 1

def setup(bot):
    bot.add_cog(Fun(bot))
