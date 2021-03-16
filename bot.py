import sqlite3
from pathlib import Path
import discord
from discord.ext import commands

prefix = "<<"
bot = commands.Bot(command_prefix=prefix, owner_id=276462585690193921)
bot.remove_command('help')
Discord_Bot_Dir = Path("./")
linksPath = Path(Discord_Bot_Dir/"links/")

@bot.event
async def on_ready():
    db = sqlite3.connect('data/main.sqlite')
    cursor = db.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS daydeal(
            daydeal_id INTEGER PRIMARY KEY,
            guild_id TEXT,
            channel_id TEXT,
            role_id TEXT
        )
    ''')
    activity = discord.Activity(type=discord.ActivityType.listening, name=f"{prefix}help")
    await bot.change_presence(activity=activity)
    await load_extensions()
    print(f'[bot.py] {bot.user} has connected')

startup_extensions = ['gif','music','duel','daydeal','epicGames','util','giveaway','fun']

async def load_extensions():
    for extension in startup_extensions:
        try:
            bot.load_extension(f'modules.{extension}')
        except Exception as e:
            exc = f'{type(e).__name__}: {e}'
            print(f'Failed to load extension {extension}\n{exc}')

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
        embed.add_field(name='Daydeal', value=f'``{prefix}help daydeal``')
        embed.add_field(name='Duel', value=f'``{prefix}help duel``')
        embed.add_field(name='Owner', value=f'``{prefix}help owner``')
        await ctx.channel.send(embed=embed)

@help.command()
async def info(ctx):
    embed = discord.Embed(
            title="Information",
            description=f"Hello! I'm Dux-Bot. My parents are <@{str(bot.owner_id)}> and <@{str(224618877626089483)}>. Hope you will enjoy my company.",
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
async def daydeal(ctx):
    embed = discord.Embed(
            title="Daydeal",
            description=f"Super duper cool https://daydeal.ch integration in discord",
            colour = discord.Colour.green()
        )
    embed.add_field(name="`deal`",value="Sends current daydeal", inline=False)
    embed.add_field(name="`setupDaydeal`",value=f"Setups the daydeal to send it whenever a new one is available. us it like '{prefix}setupDaydeal [channel] [roleToPing]'. You need 'manage_channels' permission to use this command.", inline=False)
    embed.add_field(name="`stopDaydeal`",value="Stops automatic sending od daydeals", inline=False)
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

@help.command()
async def owner(ctx):
    embed = discord.Embed(
            title="Owner",
            description=f"Some commands for the bot owner.",
            colour = discord.Colour.greyple()
        )
    embed.add_field(name="`sysinfo`",value="Shows host RAM and CPU usage", inline=False)
    embed.add_field(name="`run_command`",value="Run console commands remotely", inline=False)
    await ctx.channel.send(embed=embed)

file = open(Discord_Bot_Dir / 'token.txt', 'rt')
bot.run(str(file.read()))
