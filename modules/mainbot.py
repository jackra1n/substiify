import sqlite3
import discord
from discord.ext import commands
import json

class MainBot(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        with open("./data/settings.json", "r") as settings:
            self.settings = json.load(settings)
        self.startup_extensions = [
            'gif',
            # 'music',
            'duel',
            'daydeal',
            'epicGames',
            'util',
            'giveaway',
            'fun',
            'help'
        ]

    async def load_extensions(self):
        for extension in self.startup_extensions:
            try:
                self.bot.load_extension('modules.'+extension)
            except Exception as e:
                exc = f'{type(e).__name__}: {e}'
                print(f'Failed to load extension {extension}\n{exc}')

    async def load_db(self):
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

    @commands.Cog.listener()
    async def on_ready(self):
        await self.bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name=f"{self.settings['prefix']}help"))
        await self.load_db()
        await self.load_extensions()
        print(f'[bot.py] {self.bot.user} has connected')

def setup(bot):
    bot.add_cog(MainBot(bot))
