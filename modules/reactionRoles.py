import aiofiles
import discord
import random
import json
from discord.utils import get
from discord.ext.commands import Cog, command

class ReactionRoles(Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bot.reaction_roles = []

    @Cog.listener()
    async def on_ready(self):
        async with aiofiles.open('reaction_roles.txt', 'a') as temp:
            pass

        async with aiofiles.open('reaction_roles.txt', 'r') as file:
            lines = await file.readlines()
            for line in lines:
                data = line.split(" ")
                self.bot.reaction_roles.append((int(data[0]), int(data[1]), data[2].strip("\n")))
           

    @Cog.listener()
    async def on_raw_reaction_add(self, payload):
        for role_id, msg_id, emoji in self.bot.reaction_roles:
            if emoji.startswith("b'<"):
                print("pogu")
                emojiCrop = emoji[2:-1]
            if emojiCrop == str(payload.emoji.name):
                print("it works")
            else:
                print("emojiCrop: "+emojiCrop+" , payload.emoji.name: "+payload.emoji.name)
            if msg_id == payload.message_id and str(emoji) == str(payload.emoji.name.encode("utf-8")):
                await payload.member.add_roles(self.bot.get_guild(payload.guild_id).get_role(role_id))

    @Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        for role_id, msg_id, emoji in self.bot.reaction_roles:
            if msg_id == payload.message_id and emoji == str(payload.emoji.name.encode("utf-8")):
                guild = self.bot.get_guild(payload.guild_id)
                await guild.get_member(payload.user_id).remove_roles(guild.get_role(role_id))


    @command()
    async def set_reaction(self, ctx, role: discord.Role=None, msg: discord.Message=None, emoji=None):
        if role != None and msg != None and emoji != None:
            await msg.add_reaction(emoji)
            print(emoji)
            self.bot.reaction_roles.append((role.id, msg.id, str(emoji.encode("utf-8"))))
            async with aiofiles.open("reaction_roles.txt", mode="a") as file:
                emoji_utf = emoji.encode("utf-8")
                await file.write(f"{role.id} {msg.id} {emoji_utf}\n")

            await ctx.channel.send("Reaction has been set.")
            
        else:
            await ctx.send("Invalid arguments.")

def setup(bot):
    bot.add_cog(ReactionRoles(bot))