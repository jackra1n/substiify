from discord.ext import commands
from utils.store import store
from utils import util
import discord
import json
import logging

logger = logging.getLogger(__name__)

class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        with open(store.settings_path, "r") as settings:
            self.settings = json.load(settings)
        self.prefix = util.prefixById(self.bot)

    @commands.group(invoke_without_command = True)
    async def help(self, ctx):
        await ctx.message.delete()
        embed = discord.Embed(
            title=f'{self.bot.user.display_name} Command List',
            colour = discord.Colour.red()
        )
        categories = ['modules', 'music', 'votes', 'giveaway', 'util', 'submit', 'duel']
        if await self.bot.is_owner(ctx.author):
            categories.append('owner') 
        embed.add_field(name='Available categories:', value=await self.help_string(categories))
        embed.set_footer(text=f'Use: `{self.prefix}help <category>`')
        await ctx.send(embed=embed)

    async def help_string(self, categories):
        mainString = ''
        for c in categories:
            mainString += f'`{c}`'
            if c != categories[-1]:
                mainString += f', '
        return mainString

    @help.command()
    async def modules(self,ctx):
        embed = discord.Embed(
            title="Modules manager",
            description=f"Allows you to enable and disable some commands",
            colour = discord.Colour.greyple()
        )
        embed.add_field(name="`list`",value="Shows all the modules that can be toggled and their status", inline=False)
        embed.add_field(name="`toggle`",value="Disables or enables module depending on its current state ", inline=False)
        embed.set_footer(text=f'Use: `{self.prefix}module <command>`')
        await ctx.send(embed=embed, delete_after=120)

    @help.command()
    async def submit(self,ctx):
        embed = discord.Embed(
            title="Submissions",
            description=f"Submit a bug or a suggestion to improve the bot",
            colour = discord.Colour.greyple()
        )
        embed.add_field(name="`submit bug`",value=f'If you find any bugs/error you can use this command to submit the bug to the dev team. Use: `{self.prefix}submit bug <text_describing_bug>`.', inline=False)
        embed.add_field(name="`submit suggestion`",value=f'Use this command you have any idea for improvement or change that will make something better. Use: `{self.prefix}submit suggestion <suggestion_for_change_or_improvement>`.', inline=False)
        await ctx.send(embed=embed, delete_after=120)

    @help.command()
    async def duel(self,ctx):
        embed = discord.Embed(
            title="Duel",
            description=f"To start a duel use command `{self.prefix}fight <userOfYourChoice>` and ping a person you want to fight. There are 3 classes and each one has different stats. There is Berserker, Tank and Wizard. ",
            colour = discord.Colour.greyple()
        )
        embed.add_field(name='Stats', value="```Statistics: Berserker  Tank  Wizard\n"+
                                            "Health:       1000     1200    700\n"+
                                            "Max Attack:   140      100     200\n"+
                                            "Max Defense:  30       60      20\n"+
                                            "Max Mana:     30       20      50```", inline=False)
        embed.add_field(name='Description', value="When the duel starts you will be able to choose action you want to do. `punch`, `defend` and `end`. `punch` boosts your attack and `defend` boosts your defense. After you choose an action, you will hit the opponent and he will counter attack. If the defense is higher than the attack damage of the opponent you will block the attack. `end` makes you surrender.", inline=False)
        await ctx.send(embed=embed, delete_after=120)

    @help.command()
    async def music(self,ctx):
        embed = discord.Embed(
            title="Music",
            description=f"Music module commands.",
            colour = discord.Colour.greyple()
        )
        embed.add_field(name="`play`,`p [query or link]`", value='Play music or add to queue')
        embed.add_field(name="`skip`,`next`", value='Skip currently played song')
        embed.add_field(name="`pause`", value='Pause the song song')
        embed.add_field(name="`resume`", value='Resume playing (when paused)')
        embed.add_field(name="`stop`,`leave`", value='Stop playing music and leave (deletes queue)')
        embed.add_field(name="`shuffle`", value='Shuffles palylist')
        embed.add_field(name="`queue`, `q`", value='Shows current song queue')
        embed.add_field(name="`q move [from_index] [to_index]`", value='Move song from one index to another')
        embed.add_field(name="`q track/song [index]`", value='Shows info about song in queue')
        embed.add_field(name="`now`, `currentsong`", value='Shows currently played song')
        embed.add_field(name="`repeat [1, all, none]`", value='Repeat current song, all songs or none')
        embed.add_field(name="`lyrics`", value='Shows lyrics of currently played song. Doesn\'t work very well as of now.')
        await ctx.send(embed=embed, delete_after=120)

    @help.command()
    async def giveaway(self, ctx):
        embed = discord.Embed(
            title="Giveaway",
            colour = discord.Colour.greyple()
        )
        embed.add_field(name="`giveaway create`",value="Initializes setup for a giveaway. After this command you will be asked for more info.", inline=False)
        embed.add_field(name="`giveaway reroll`",value=f'Allows you to "re-roll" giveaway. This function takes channel and id of the giveaway message as parameters. Example: `{self.prefix}giveaway reroll <channel_mention> <msg_id>`', inline=False)
        await ctx.send(embed=embed, delete_after=120)
    
    @help.command()
    async def votes(self,ctx):
        embed = discord.Embed(
            title="Voting system",
            description=f"Like Reddits voting or youtubes like but for discordd",
            colour = discord.Colour.greyple()
        )
        embed.add_field(name="`votes`", value=f'Tells you if the current channel has voting system enabled', inline=False)
        embed.add_field(name="`votes setup`", value=f'Activates voting in a channel. Use: `{self.prefix}vote setup <channel_id>`. Parameter channel_id is optional. If no parameter provided voting will be enabled for the current channel.', inline=False)
        embed.add_field(name="`votes stop`", value=f'Stops voting system. Use: `{self.prefix}vote stop <channel_id>`. Parameter channel_id is optional. If no parameter provided voting will be stopped in the current channel.', inline=False)
        await ctx.send(embed=embed, delete_after=120)

    @help.command()
    async def util(self,ctx):
        embed = discord.Embed(
            title="Util",
            description=f"Useful commands that can help you organize your server",
            colour = discord.Colour.greyple()
        )
        embed.add_field(name="`av`",value=f'Shows user avatar. `{self.prefix}av` shows your avatar. `{self.prefix}av <id/mention>` shows avatar of other user.', inline=False)
        embed.add_field(name="`info`",value=f'Shows some infos about the bot like uptime, versions etc.', inline=False)
        embed.add_field(name="`clear`",value=f'Clears last X messages in the channel. Use: `{self.prefix}clear <amount_of_messages>`', inline=False)
        embed.add_field(name="`clear message`",value=f'Clears message with given ID. Use: `{self.prefix}clear message <message_id>`', inline=False)
        embed.add_field(name="`ping`",value=f'Ping between bot and discord', inline=False)
        await ctx.send(embed=embed, delete_after=120)

    @help.command()
    @commands.is_owner()
    async def owner(self,ctx):
        embed = discord.Embed(
            title="Owner",
            description=f"Commands for the bot owner",
            colour = discord.Colour.greyple()
        )
        embed.add_field(name="`shutdown`",value=f'Shuts down the bot', inline=False)
        embed.add_field(name="`reload`",value=f'Does git pull and reloads cogs', inline=False)
        embed.add_field(name="`status count`",value=f'Allows you to set count of the servers in the bot status. Use: `{self.prefix}status count <number>`', inline=False)
        embed.add_field(name="`status set`",value=f'Allows you to set completely custom bot status. Use: `{self.prefix}status set <text>`', inline=False)
        embed.add_field(name="`status reset`",value=f'Resets the bot status to the original one.', inline=False)
        embed.add_field(name="`version`",value=f'Set version of the bot. Use: `{self.prefix}version <version>`', inline=False)
        embed.add_field(name="`server list`",value=f'Show the list of servers that the bot is in. Shows server name, amount of users and server id.', inline=False)
        await ctx.send(embed=embed, delete_after=20)

def setup(bot):
    bot.add_cog(Help(bot))
