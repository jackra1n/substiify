from discord.ext import commands
from utils.prepare import createFiles
from utils.store import store
import json

createFiles()

with open(store.settings_path, "r") as settings:
    settings = json.load(settings)
    
bot = commands.Bot(command_prefix=settings['prefix'], owner_id=276462585690193921)

bot.remove_command('help')
bot.load_extension("modules.mainbot")

if not settings['token']:
    print(f'No token in {store.settings_path}! Please add it and try again.')
    exit()

bot.run(settings['token'])
