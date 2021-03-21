from discord.ext import commands
from utils.prepare import createFiles
import json

createFiles()

with open("./data/settings.json", "r") as settings:
    settings = json.load(settings)
    
bot = commands.Bot(command_prefix=settings['prefix'], owner_id=276462585690193921)

bot.remove_command('help')
bot.load_extension("modules.mainbot")

if settings['token'] is None:
    print('No token in ./data/settings.json! Please add it and try again.')
    exit()

bot.run(settings['token'])
