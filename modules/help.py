import discord
import time
import json
import logging
from utils.store import store
from pathlib import Path
from discord.ext import commands

class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        with open(store.settings_path, "r") as settings:
            self.settings = json.load(settings)
        self.prefix = self.settings['prefix']

    @commands.command()
    async def help(self,ctx):
        if ctx.invoked_subcommand is None:
            embed = discord.Embed(
                    title=f'{self.bot.user.display_name} Command List',
                    colour = discord.Colour.red()
                )
            categories = ['info', 'gifs', 'fun', 'daydeal', 'duel', 'owner', 'music']
            embed.add_field(name='Available categories:', value=await self.help_string(categories))
            await ctx.send(embed=embed)

    async def help_string(self, categories):
        mainString = ''
        for c in categories:
            mainString += f'`{c}`'
            if c != categories[-1]:
                mainString += f', '
        return mainString

    @commands.command()
    async def gifs(self,ctx):
        embed = discord.Embed(
                title="Gifs",
                description=f"Use any of the available gif commands and tag a person in order to send a GIF of that action",
                colour = discord.Colour.greyple()
            )
        embed.add_field(name="**Possible categories:** ",value="`slap`, `hug`, `cuddle`, `kiss`, `bite`")
        await ctx.send(embed=embed)

    @commands.command()
    async def fun(self,ctx):
        embed = discord.Embed(
                title="Gifs",
                description=f"Some fun command to play around.",
                colour = discord.Colour.greyple()
            )
        embed.add_field(name="`pp`",value="Tells how long is your pp :)", inline=False)
        embed.add_field(name="`pickup`",value="Wanna hit on someone? Let me be your wingman! Most of them are inappropriate so please use it on people you know well!", inline=False)
        embed.add_field(name="`roast`",value="Insult someone until they cry", inline=False)
        embed.add_field(name="`8ball`",value="Ask the bot a question that you dont want the answer to.", inline=False)
        await ctx.send(embed=embed)

    @commands.command()
    async def daydeal(self,ctx):
        embed = discord.Embed(
                title="Daydeal",
                description=f"Super duper cool https://daydeal.ch integration in discord",
                colour = discord.Colour.green()
            )
        embed.add_field(name="`deal`",value="Sends current daydeal", inline=False)
        embed.add_field(name="`setupDaydeal`",value=f"Setups the daydeal to send it whenever a new one is available. Use it like `{self.prefix}setupDaydeal [channel] [roleToPing]`. Channel and role are optional. Requires'manage_channels' permission to use this command.", inline=False)
        embed.add_field(name="`stopDaydeal`",value="Stops automatic sending od daydeals", inline=False)
        await ctx.send(embed=embed)

    @commands.command()
    async def duel(self,ctx):
        embed = discord.Embed(
                title="Duel",
                description=f"To start a duel use command `{self.prefix}fight userOfYourChoice` and ping a person you want to fight. There are 3 classes and each one has different stats. There is Berserker, Tank and Wizard. ",
                colour = discord.Colour.greyple()
            )
        embed.add_field(name='Stats', value="```Statistics: Berserker  Tank  Wizard\n"+
                                            "Health:       1000     1200    700\n"+
                                            "Max Attack:   140      100     200\n"+
                                            "Max Defense:  30       60      20\n"+
                                            "Max Mana:     30       20      50```", inline=False)
        embed.add_field(name='Description', value="When the duel starts you will be able to choose action you want to do. `punch`, `defend` and `end`. `punch` boosts your attack and `defend` boosts your defense. After you choose an action, you will hit the opponent and he will counter attack. If the defense is higher than the attack damage of the opponent you will block the attack. `end` makes you surrender.", inline=False)
        await ctx.send(embed=embed)

    @commands.command()
    async def owner(self,ctx):
        embed = discord.Embed(
                title="Owner",
                description=f"Some commands for the bot owner.",
                colour = discord.Colour.greyple()
            )
        embed.add_field(name="`run_command`",value="Run console commands remotely", inline=False)
        await ctx.send(embed=embed)

    @commands.command()
    async def music(self,ctx):
        embed = discord.Embed(
                title="Music",
                description=f"Music module commands.",
                colour = discord.Colour.greyple()
            )
        embed.add_field(name="`play`", value='Play music or add to queue')
        embed.add_field(name="`skip`", value='Skip currently played song')
        embed.add_field(name="`pause`", value='Pause the song song')
        embed.add_field(name="`resume`", value='Resume playing (when paused)')
        embed.add_field(name="`stop`", value='Stop playing music and leave (deletes queue)')
        embed.add_field(name="`shuffle`", value='Shuffles palylist')
        embed.add_field(name="`queue`, `q`", value='Shows current song queue')
        embed.add_field(name="`now`, `currentsong`", value='Shows currently played song')
        await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(Help(bot))
