from utils.store import store
from discord.ext import commands
import subprocess
import sqlite3
import discord
import json

class MainBot(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        with open(store.settings_path, "r") as settings:
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
        db = sqlite3.connect(store.db_path)
        cursor = db.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS daydeal(
                id INTEGER PRIMARY KEY,
                guild_id INTEGER,
                channel_id INTEGER,
                role_id INTEGER
            )
        ''')

    @commands.Cog.listener()
    async def on_ready(self):
        await self.bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name=f"{self.settings['prefix']}help"))
        await self.load_db()
        await self.load_extensions()
        print(f'[bot.py] {self.bot.user} has connected')

    @commands.command()
    async def reload(self, ctx):
        if ctx.author.id == self.bot.owner_id:
            self.bot.get_cog('Daydeal').daydeal_task.stop()
            subprocess.run(["git","pull","--no-edit"])
            try:
                for cog in self.startup_extensions:
                    self.bot.reload_extension(f'modules.{cog}')
            except Exception as e:
                exc = f'{type(e).__name__}: {e}'
                await ctx.channel.send(f'Failed to reload extensions\n{exc}')
            await ctx.channel.send('Realoded all cogs')


def setup(bot):
    bot.add_cog(MainBot(bot))
