from discord.ext import commands
from utils.prepare import prepareFiles
from utils.db import create_database
from utils.store import store
import discord
import logging
import json

prepareFiles()
create_database()

with open(store.settings_path, "r") as settings:
    settings = json.load(settings)

intents = discord.Intents()
bot = commands.Bot(command_prefix=settings['prefix'], owner_id=276462585690193921, intents=intents.all())

bot.remove_command('help')
bot.load_extension("modules.mainbot")

if not settings['token']:
    logging.error(f'No token in {store.settings_path}! Please add it and try again.')
    exit()

bot.run(settings['token'])
