from utils.store import store
from discord.ext import commands
from discord import Activity, ActivityType
from utils import db, util
import subprocess
import logging
import json

logger = logging.getLogger(__name__)

class MainBot(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        with open(store.settings_path, "r") as settings:
            self.settings = json.load(settings)
        self.startup_extensions = [
            'gif',
            'music',
            'duel',
            'daydeal',
            'epicGames',
            'util',
            'giveaway',
            'fun',
            'draw',
            'help'
        ]

    async def load_extensions(self):
        for extension in self.startup_extensions:
            try:
                self.bot.load_extension('modules.'+extension)
            except Exception as e:
                exc = f'{type(e).__name__}: {e}'
                logger.warning(f'Failed to load extension {extension}\n{exc}')

    @commands.Cog.listener()
    async def on_ready(self):
        servers = len(self.bot.guilds)
        self.prefix = util.prefixById(self.bot)
        activityName = f"{self.prefix}help | {servers} servers"
        activity = Activity(type=ActivityType.listening, name=activityName)
        await self.bot.change_presence(activity=activity)
        await self.load_extensions()
        logger.info(f'Connected as -> [{self.bot.user}]')

    @commands.Cog.listener()
    async def on_message(self, message):
        if self.bot.is_ready() and message.content.startswith(self.prefix) :
            db.session.add(db.command_history(message))
            db.session.commit()

    @commands.Cog.listener()
    async def on_command_completion(self, ctx):
        logger.info(f'command [{ctx.message.content[len(self.prefix):]}] executed for -> [{ctx.author}]')

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        await ctx.message.add_reaction('🆘')
        logger.error(f'command failed to executed for [{ctx.author}] <-> [{error}]')

    @commands.command()
    @commands.is_owner()
    async def reload(self, ctx):
        self.bot.get_cog('Daydeal').daydeal_task.stop()
        subprocess.run(["git","pull","--no-edit"])
        try:
            for cog in self.startup_extensions:
                self.bot.reload_extension(f'modules.{cog}')
        except Exception as e:
            exc = f'{type(e).__name__}: {e}'
            await ctx.channel.send(f'Failed to reload extensions\n{exc}')
        await ctx.channel.send('Reloaded all cogs')

def setup(bot):
    bot.add_cog(MainBot(bot))
