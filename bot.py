from discord.ext import commands
from colour import Color
from pathlib import Path
import datetime
import discord
import random
import psutil
import json
import time
import os

bot = commands.Bot(command_prefix=',')
bot.remove_command('help')
Discord_Bot_Dir = Path("./")
linksPath = Path(Discord_Bot_Dir/"links/")

marshDiscordId = 224618877626089483
jackDiscordId = 276462585690193921

@bot.event
async def on_ready():
    activity = discord.Activity(type=discord.ActivityType.listening, name=",help")
    await bot.change_presence(activity=activity)
    print("="*20)
    print("Logged in as "+bot.user.name)
    print("="*20)

@bot.group()
async def help(ctx):
    if ctx.invoked_subcommand is None:
        embed = discord.Embed(
                title="HomieBot Command List",
                description='Those are availble categories:',
                colour = discord.Colour.red()
            )
        # embed.add_field(name='Fun', value='``.help fun``', inline=True)
        embed.add_field(name='Info', value='``.help info``', inline=True)
        embed.add_field(name='Duel', value='``.help duel``', inline=True)
        await ctx.channel.send(embed=embed)

@help.command()
async def info(ctx):
    embed = discord.Embed(
            title="Information",
            description="Hello! I'm HomieBot. My parents are <@{}> and <@{}>. Hope you will enjoy my company.".format(str(jackDiscordId), str(marshDiscordId)),
            colour = discord.Colour.greyple()
        )
    await ctx.channel.send(embed=embed)

@help.command()
async def duel(ctx):
    embed = discord.Embed(
            title="Duel",
            description="To start a duel use command '.fight "+bot.user.mention+"' and ping a person you want to fight. There are 3 classes and each one has different stats. There is Berserker, Tank and Wizard. ",
            colour = discord.Colour.greyple()
        )
    embed.add_field(name='Stats', value="```Statistics: Berserker  Tank  Wizard\n"+
                                        "Health:       1000     1200    700\n"+
                                        "Max Attack:   140      100     200\n"+
                                        "Max Defense:  30       60      20\n"+
                                        "Max Mana:     30       20      50```", inline=False)
    embed.add_field(name='Description', value="When the duel starts you will be able to choose action you want to do. ``punch``, ``defend`` and ``end``. ``punch`` boosts your attack and ``defend`` boosts your defense. After you choose an action, you will hit the opponent and he will counter attack. If the defense is higher than the attack damage of the opponent you will block the attack. ``end`` makes you surrender.", inline=False)
    await ctx.channel.send(embed=embed)

@bot.command()
async def system_info(ctx):
    if ctx.message.author.id == jackDiscordId:
        cpu_usage = psutil.cpu_percent()
        ramTotal = psutil.virtual_memory().total >> 20
        ramAvailable = psutil.virtual_memory().available >> 20
        color_list = list(Color("green").range_to(Color("red"),100))
        color = int("0x"+str(color_list[int(cpu_usage)].hex)[1:], 16)
        embed = discord.Embed(
                title="System usage information",
                colour = discord.Colour(color)
            )
        embed.add_field(name="CPU", value=f"Current CPU usage is: {cpu_usage}%")
        embed.add_field(name="RAM", value=f"Current RAM usage is: {ramTotal-ramAvailable}/{ramTotal}MB")
        await ctx.channel.send(embed=embed)

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        pass

@bot.command(brief='In Progress 😊')
async def cd(ctx):
    Tday = datetime.date.today()
    f_date = datetime.date(2020, 8, 10)
    delta = f_date - Tday
    if ctx.author.id == marshDiscordId or ctx.author.id == 704589853974855770 or ctx.author.id == jackDiscordId:
        await ctx.channel.send(delta)

@bot.command(aliases=['8ball'], brief='AKA 8ball, Ask the bot a question that you dont want the answer to.')
async def eightball(ctx,*,question):
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
    await ctx.channel.send(f'Question: {question}\nAnswer: {random.choice(responses)}')

@bot.command(brief='Clears messages within the current channel.')
@commands.has_permissions(manage_messages=True)
async def clear(ctx,amount):
    amount = int(amount)
    if amount <= 100:
        await ctx.channel.purge(limit=amount + 1)
    else:
        await ctx.channel.send('Cannot delete more than 100 messages at a time!')

@clear.error
async def clear_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
      await ctx.channel.send('Please put an amount to clear.')

@bot.command(aliases=['penis','pipa','pene'], brief='Ego problems? No problem I can help you with that.')
async def pp(ctx, member : discord.Member=None):
    member = ctx.author if member is None else member
    no_use_pp = None
    PP_Size = random.randint(3,20)
    if member.id == 488959709609590787:
        member = no_use_pp
    if member.id == jackDiscordId:
        PP_Size = 20
    elif member.id == 464861706665984010:
        PP_Size = 1
    embed = discord.Embed(
        title = 'AYE DAWG NICE PEEPEE!',
        description = str(member.name) + '\'s penis size is ' + str(PP_Size) + 'cm 😘\n8' + ("=" * PP_Size) + 'D',
        colour = discord.Colour.magenta()
    )
    await ctx.channel.send(embed=embed)

@bot.command(aliases=['insult','burn'], brief='Insult someone until they cry')
async def roast(ctx, member : discord.Member=None):
    member = ctx.author if member is None else member
    author = bot.user if member is ctx.author else ctx.author
    if bot.user.id == member.id:
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
            title = 'HOMIE INSULTS! 🔥',
            description = str(author.name) + ' says: ay ' + str(member.name) + ', ' + await lineChooser("insults.txt"),
            colour = discord.Colour.orange()
        )
        await ctx.channel.send(embed=embed)
        file.close()

@bot.command(brief='Wanna hit on someone? Let me be your wingman!')
async def pickup(ctx, member : discord.Member=None):
    member = ctx.author if member is None else member
    author = bot.user if member is ctx.author else ctx.author
    embed = discord.Embed(
        title = 'HOMIE PICKUPS! 🌈',
        description = str(author.name) + ' says: ay ' + str(member.name) + ', ' + await lineChooser("pickup.txt"),
        colour = discord.Colour.orange()
    )
    await ctx.channel.send(embed=embed)
    file.close()

async def lineChooser(filename):
    lines = open(linksPath / filename).read().splitlines()
    return random.choice(lines)

@bot.command(brief='Enlarge and view your profile picture or another member')
async def av(ctx, member : discord.Member=None):
    member = ctx.author if member is None else member
    embed = discord.Embed(
        title = str(member.name),
        description = 'Avatar',
        colour = discord.Colour.light_grey()
    )
    embed.set_image(url=member.avatar_url)
    await ctx.channel.send(embed=embed)

startup_extensions = ["modules.gif","modules.music","modules.duel","modules.daydeal"]

if __name__ == "__main__":
    for extension in startup_extensions:
        try:
            bot.load_extension(extension)
        except Exception as e:
            exc = '{}: {}'.format(type(e).__name__, e)
            print('Failed to load extension {}\n{}'.format(extension, exc))

file = open(Discord_Bot_Dir / 'token.txt','rt')
bot.run(str(file.read()))