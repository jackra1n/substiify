from discord.ext import commands
from os import walk, path

from helper.ModulesManager import ModuleDisabledException
from utils.store import store
from utils import db, util

import logging
import json

logger = logging.getLogger(__name__)

class MainBot(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        with open(store.settings_path, "r") as settings:
            self.settings = json.load(settings)
        self.startup_extensions = self.get_modules()

    def get_modules(self):
        filenames = next(walk("modules"), (None, None, []))[2] 
        filenames.remove(path.basename(__file__))
        return [name.replace('.py','') for name in filenames]

    async def load_extensions(self):
        for extension in self.startup_extensions:
            try:
                self.bot.load_extension('modules.'+extension)
            except Exception as e:
                exc = f'{type(e).__name__}: {e}'
                logger.warning(f'Failed to load extension {extension}\n{exc}')

    @commands.Cog.listener()
    async def on_ready(self):
        self.prefix = util.prefixById(self.bot)
        await self.load_extensions()
        logger.info(f'Connected as -> [{self.bot.user}]')

    @commands.Cog.listener()
    async def on_message(self, message):
        try:
            if self.bot.is_ready() and message.content.startswith(self.prefix):
                db.session.add(db.command_history(message))
                db.session.commit()
        except AttributeError:
            self.prefix = util.prefixById(self.bot)

    @commands.Cog.listener()
    async def on_command_completion(self, ctx):
        logger.info(f'[{ctx.command.qualified_name}] executed for -> [{ctx.author}]')

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if 'is not found' in str(error) or isinstance(error, ModuleDisabledException):
            return
        await ctx.message.add_reaction('🆘')
        logger.error(f'[{ctx.command.qualified_name}] failed for [{ctx.author}] <-> [{error}]')

def setup(bot):
    bot.add_cog(MainBot(bot))
