from discord.ext import commands
from utils.db import create_database
from utils.store import store
from utils import util
import discord
import logging
import json

util.prepareFiles()
create_database()
logger = logging.getLogger(__name__)

with open(store.settings_path, "r") as settings:
    settings = json.load(settings)

prefix = ";"
bot = commands.Bot(command_prefix=prefix, owner_id=276462585690193921, intents=discord.Intents().all())

bot.remove_command('help')
bot.load_extension("modules.mainbot")

if not settings['token']:
    logger.error(f'No token in {store.settings_path}! Please add it and try again.')
    exit()

bot.run(settings['token'])
