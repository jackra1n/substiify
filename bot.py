import random
from pathlib import Path

import discord
from discord.ext import commands

prefix = "<<"
bot = commands.Bot(command_prefix=prefix)
bot.remove_command('help')
Discord_Bot_Dir = Path("./")
linksPath = Path(Discord_Bot_Dir/"links/")

marshDiscordId = 224618877626089483
jackDiscordId = 276462585690193921

@bot.event
async def on_ready():
    activity = discord.Activity(type=discord.ActivityType.listening, name=f"{prefix}help")
    await bot.change_presence(activity=activity)
    print("="*20)
    print("Logged in as "+bot.user.name)
    print("="*20)

@bot.group()
async def help(ctx):
    if ctx.invoked_subcommand is None:
        embed = discord.Embed(
                title="Dux-Bot Command List",
                description='Those are availble categories:',
                colour = discord.Colour.red()
            )
        embed.add_field(name='Info', value=f'``{prefix}help info``')
        embed.add_field(name='Gifs', value=f'``{prefix}help gifs``')
        embed.add_field(name='Fun', value=f'``{prefix}help fun``')
        embed.add_field(name='Duel', value=f'``{prefix}help duel``')
        await ctx.channel.send(embed=embed)

@help.command()
async def info(ctx):
    embed = discord.Embed(
            title="Information",
            description=f"Hello! I'm Dux-Bot. My parents are <@{str(jackDiscordId)}> and <@{str(marshDiscordId)}>. Hope you will enjoy my company.",
            colour = discord.Colour.greyple()
        )
    await ctx.channel.send(embed=embed)

@help.command()
async def gifs(ctx):
    embed = discord.Embed(
            title="Gifs",
            description=f"Use any of the available gif commands and tag a person in order to send a GIF of that action",
            colour = discord.Colour.greyple()
        )
    embed.add_field(name="**Possible categories:** ",value="``slap``, ``hug``, ``cuddle``, ``kiss``, ``bite``")
    await ctx.channel.send(embed=embed)

@help.command()
async def fun(ctx):
    embed = discord.Embed(
            title="Gifs",
            description=f"Some fun command to play around.",
            colour = discord.Colour.greyple()
        )
    embed.add_field(name="`pp`",value="Tells how long is your pp :)", inline=False)
    embed.add_field(name="`pickup`",value="Wanna hit on someone? Let me be your wingman! Most of them are inappropriate so please use it on people you know well!", inline=False)
    embed.add_field(name="`roast`",value="Insult someone until they cry", inline=False)
    embed.add_field(name="`8ball`",value="AKA 8ball, Ask the bot a question that you dont want the answer to.", inline=False)
    await ctx.channel.send(embed=embed)

@help.command()
async def duel(ctx):
    embed = discord.Embed(
            title="Duel",
            description=f"To start a duel use command '{prefix}fight userOfYourChoice' and ping a person you want to fight. There are 3 classes and each one has different stats. There is Berserker, Tank and Wizard. ",
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
async def jack(ctx):
    await ctx.channel.send('"Fucking Jack!"')

@commands.cooldown(6, 5)
@bot.command()
async def pp(ctx, member : discord.Member=None):
    member = ctx.author if member is None else member
    PP_Size = random.randint(3,20)
    if member.id == jackDiscordId:
        PP_Size = 20
    embed = discord.Embed(
        title = 'AYE DAWG NICE PEEPEE!',
        description = str(member.name) + '\'s pp size is ' + str(PP_Size) + 'cm 😘\n8' + ("=" * PP_Size) + 'D',
        colour = discord.Colour.magenta()
    )
    await ctx.channel.send(embed=embed)

@commands.cooldown(6, 5)
@bot.command(brief='Wanna hit on someone? Let me be your wingman!')
async def pickup(ctx, member : discord.Member=None):
    member = ctx.author if member is None else member
    author = bot.user if member is ctx.author else ctx.author
    embed = discord.Embed(
        title = 'BOT PICKUPS! 🌈',
        description = str(author.name) + ' says: ay ' + str(member.name) + ', ' + await lineChooser("pickup.txt"),
        colour = discord.Colour.orange()
    )
    await ctx.channel.send(embed=embed)
    file.close()

async def lineChooser(filename):
    lines = open(linksPath / filename).read().splitlines()
    return random.choice(lines)

@commands.cooldown(6, 5)
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
            title = 'BOT INSULTS! 🔥',
            description = str(author.name) + ' says: ay ' + str(member.name) + ', ' + await lineChooser("insults.txt"),
            colour = discord.Colour.orange()
        )
        await ctx.channel.send(embed=embed)
        file.close()

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        pass

@commands.cooldown(6, 5)
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

startup_extensions = ["modules.gif", "modules.music", "modules.duel", "modules.daydeal", "modules.epicGames", "modules.util", "modules.giveaway"]

if __name__ == "__main__":
    for extension in startup_extensions:
        try:
            bot.load_extension(extension)
        except Exception as e:
            exc = '{}: {}'.format(type(e).__name__, e)
            print('Failed to load extension {}\n{}'.format(extension, exc))

file = open(Discord_Bot_Dir / 'token.txt', 'rt')
bot.run(str(file.read()))
