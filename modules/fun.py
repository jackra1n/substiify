from discord.ext import commands
from datetime import timedelta
from datetime import datetime
from utils.store import store
from pathlib import Path
import logging
import discord
import random

async def lineChooser(filename):
    lines = open(f'{store.resources_path}/{filename}').read().splitlines()
    return random.choice(lines)

class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.tips_enabled = False

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
        embed = discord.Embed(
            title=await lineChooser('8ball.txt'),
            description=f'Question: {question}',
            colour = discord.Colour.orange()
        )
        embed.set_footer(text=f'Question by {ctx.author}', icon_url=ctx.author.avatar_url)
        await ctx.channel.send(embed=embed)

    @commands.command()
    async def serversInfo(self, ctx):
        if await self.bot.is_owner(ctx.author):
            serverList = []
            userList = []
            for guild in self.bot.guilds:
                serverList.append(f'{guild.name}::{guild.id}')
                userList.append(f'{guild.name} has {guild.member_count}')
            await ctx.send(f'{serverList}\n{userList}')

    @commands.command()
    async def tips(self, ctx):
        if await self.bot.is_owner(ctx.author):
            if 'enable' in ctx.message.content:
                self.tips_enabled = True
            elif 'disable' in ctx.message.content:
                self.tips_enabled = False

    @commands.command()
    async def findUsers(self, ctx, pattern, serverId: int = None):
        if await self.bot.is_owner(ctx.author):
            if serverId is None:
                serverId = ctx.guild.id
            owner = await self.bot.fetch_user(self.bot.owner_id)
            matches = await self.find_matches(ctx, pattern, serverId)
            matches_text = ''
            for user in matches:
                matches_text += f'{str(user)}: {user.nick}\n'
            text = f'Here are matches:```{matches_text}```'
            await owner.send(text)


    async def find_matches(self, ctx, pattern, serverId: int):
        pattern = pattern[1:-1]
        user_list = [user for user in await self.bot.get_guild(serverId).fetch_members().flatten() if not user.bot]
        matches = []
        same_length = lambda x: len(str(x)) == len(str(pattern))
        for user in filter(same_length, user_list):
            for i in range(len(str(user))):
                if pattern[i] == "_":
                    continue
                if pattern[i] != str(user)[i]:
                    break
                else:
                    matches.append(user)
        return matches

    @commands.Cog.listener()
    async def on_message(self, message):
        gameText = 'has the thing'
        eth_serverId = 747752542741725244
        if gameText in message.content and message.author.id == 778731540359675904 and message.guild.id == eth_serverId and self.tips_enabled:
            ctx = await self.bot.get_context(message)
            owner = await self.bot.fetch_user(self.bot.owner_id)
            holder = message.content.split('seconds.\n',1)[1].split(' has',1)[0]
            matches = self.find_matches(ctx, holder, eth_serverId)
            # last_10_days = (datetime.now() - timedelta(days=10))
            # for match in matches:
            #     if not await match.history(after=last_10_days, limit=10).flatten():
            #         matches.remove(match)
            matches_text = ''
            for user in matches:
                matches_text += f'{str(user)}: {user.nick}\n'
            text = f'Here are matches:```{matches_text}```'
            await owner.send(text)
            await asyncio.sleep(110)
            await owner.send('You can grab thing in 10 seconds!')
            await asyncio.sleep(8)
            await owner.send('NOW!')

def setup(bot):
    bot.add_cog(Fun(bot))
