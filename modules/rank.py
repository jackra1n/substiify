from discord.ext import commands
import random

from helper.LastMessageList import LastMessageList

class Rank(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.lml = LastMessageList() # Last message list

    # check if there was a message sent in tht last minute
    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return
        if message.author.id == self.bot.user.id:
            return
        if message.content.startswith(self.bot.command_prefix):
            return

        # get the guild's id
        guild_id = message.guild.id

        # get the current time
        current_time = message.created_at.timestamp()

        user = message.author
        # get the last message of a user
        if self.lml.getLastMessageByUserAndServer(message.author, message.guild) is None or user.last_message.created_at.timestamp() + 60 < current_time:
            self.lml.add_message(guild_id, user, message)

        # check if the last message was sent in the last minute
        if (current_time - user.last_message.created_at.timestamp()) < 60:
            return

        rank_points = random.randrange(3, 5)
        

