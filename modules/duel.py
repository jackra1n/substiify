from discord.ext.commands.cooldowns import BucketType
from discord.ext import commands
from enum import Enum
import discord
import logging
import asyncio
import random

logger = logging.getLogger(__name__)

class Duel(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(brief='Fight someone on this server!')
    @commands.max_concurrency(1, per=BucketType.default, wait=True)
    async def fight(self, ctx, member: discord.Member):
        duel_authors_id = ctx.author.id
        duel_authors_name = ctx.author.display_name
        challenge_member_name = member.display_name
        challenge_member_id = member.id
        bot_id = self.bot.user.id

        # fighting yourself? Loser.
        if duel_authors_id == challenge_member_id:
            replys = ['Dumbass.. You cant challenge yourself! 🤡', 'LOL! IDIOT! 🤣',
                      'Homie... Chillax. Stop beefing with yo self 👊', 'You good bro? 😥', 'REEEEELLLAAAAXXXXXXXXX 😬',
                      'Its gonna be okay 😔']
            await ctx.channel.send(random.choice(replys))

        # fighting the bot? KEKW
        elif challenge_member_id == bot_id:
            replys = ['Simmer down buddy 🔫', 'You dare challenge thy master?! 💪', 'OK homie relax.. 💩',
                      'You aint even worth it dawg 🤏', 'You a one pump chump anyway 🤡', 'HA! Good one. 😂',
                      'You done yet? Pussy.']
            await ctx.channel.send(random.choice(replys))

        # fighting other users
        else:
            embed = discord.Embed(
                title='⚔️ ' + duel_authors_name + ' choose your class.',
                description=ctx.author.mention +
                    'what class do you want to be? `berserker`, `tank` or `wizard`?',
                colour=discord.Colour.red()
            )
            await ctx.channel.send(embed=embed)

            warrior1 = await self.createWarrior(ctx, ctx.author)

            embed = discord.Embed(
                title='⚔️ ' + duel_authors_name + ' has challenged ' + challenge_member_name + ' to a fight!',
                description=duel_authors_name + ' chose class ' + warrior1.ClassName + '. ' + member.mention +
                    ', what is your class of choice? `berserker`,`tank`, or `wizard`?\nType your choice out in chat as it is displayed!',
                colour=discord.Colour.red()
            )
            await ctx.channel.send(embed=embed)

            warrior2 = await self.createWarrior(ctx, member)
            await ctx.channel.send(
                warrior2.user.mention + ', what would like to do? `punch`,`defend`, or `end`?\nType your choice out in chat as it is displayed!')

            fight_turn = 0

            while warrior1.Health > 0 and warrior2.Health > 0:
                if await self.checkForWinner(warrior2, warrior1, ctx, fight_turn):
                    break
                if await self.checkForWinner(warrior1, warrior2, ctx, fight_turn):
                    break
            if warrior1.Health < 0:
                await self.sendWinnerEmbed(warrior2, ctx)
            elif warrior2.Health < 0:
                await self.sendWinnerEmbed(warrior1, ctx)
            else:
                await ctx.channel.send("Dude, imagine surrendering")

    async def checkForWinner(self, warrior1, warrior2, ctx, fight_turn):
        if await self.getActionResult(warrior1, warrior2, ctx) or warrior1.Health < 0 or warrior2.Health < 0:
            return True
        fight_turn += 1
        await ctx.channel.send(
            warrior2.user.mention + ', what would like to do? `punch`,`defend`, or `end`?\nType your choice out in chat as it is displayed!')

    async def sendWinnerEmbed(self, winner, ctx):
        winEmbedMessage = discord.Embed(
            title='STOP! STOP! STOP! THE FIGHT IS OVER!!!',
            description='**' + winner.user.display_name +
                '** wins with just `' + str(winner.Health) + ' HP` left!',
            colour=discord.Colour.teal()
        )
        await ctx.channel.send(embed=winEmbedMessage)

    def checkClassChooser(self, author):
        def inner_check(message):
            return (message.content == 'berserker' or message.content == 'tank' or message.content == 'wizard') and message.author == author

        return inner_check

    def checkAction(self, author):
        def inner_check(message):
            return (message.content == 'punch' or message.content == 'defend' or message.content == 'end' or (
                        message.content == "detroit smash!" and self.bot.is_owner(author))) and message.author == author
        return inner_check

    async def createWarrior(self, ctx, user):
        try:
            msgClass=await self.bot.wait_for('message', check=self.checkClassChooser(user), timeout=40.0)
            warrior=Warrior(msgClass.author)
            if msgClass.content == 'berserker':
                warrior.chooseClass(1)
            elif msgClass.content == 'tank':
                warrior.chooseClass(2)
            elif msgClass.content == 'wizard':
                warrior.chooseClass(3)
            return warrior
        except asyncio.TimeoutError:
            await ctx.channel.send('Time out!')

    async def getActionResult(self, warrior1, warrior2, ctx):
        try:
            action=await self.bot.wait_for("message", check=self.checkAction(warrior1.user), timeout=40.0)
            buff_bonus=20
            if action.content == "punch":
                attack=random.randrange(0, warrior1.AttkMax) + buff_bonus
                defense=random.randrange(0, warrior1.BlckMax)
            elif action.content == "defend":
                attack=random.randrange(0, warrior1.AttkMax)
                defense=random.randrange(0, warrior1.BlckMax) + buff_bonus
            elif action.content == "end":
                return True
            elif action.content == "detroit smash!" and await self.bot.is_owner(action.author):
                attack=random.randrange(0, warrior1.AttkMax) + 2000
                defense=random.randrange(0, warrior1.BlckMax)
            attack_damage=attack - random.randrange(warrior2.BlckMax)
            counter_damage=random.randrange(0, warrior2.AttkMax) - defense

            await self.calculateDamage(ctx, warrior1, warrior2, attack_damage)
            await self.calculateDamage(ctx, warrior2, warrior1, counter_damage)
        except asyncio.TimeoutError:
            await ctx.channel.send('action timed out!')
            return True

    async def calculateDamage(self, ctx, warrior1, warrior2, damage):
        hit_response = ['cRaZyy', 'pOwerful', 'DEADLY', 'dangerous', 'deathly', 'l33t', 'amazing']
        if damage <= 0:
            await ctx.channel.send("**" + warrior2.user.display_name + "** blocked the attack!")
        else:
            await ctx.channel.send('**' + warrior1.user.display_name + '** lands a ' + random.choice(
                hit_response) + ' hit on **' + warrior2.user.display_name + '** dealing `' + str(damage) + '` damage!')
            warrior2.Health -= damage
            await ctx.channel.send(
                '**' + warrior2.user.display_name + '**  is left with `' + str(warrior2.Health) + '` health!')

    @fight.error
    async def fight_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.channel.send('Who you tryna fight, the air?! Choose someone to fight you pleb! 🤡')


class Warrior:
    def __init__(self, user, health=1, attkMax=1, blckMax=1, mana=1, className=1):
        self.user=user
        self.Health=health
        self.AttkMax=attkMax
        self.BlckMax=blckMax
        self.Mana=mana
        self.ClassName=className

    def chooseClass(self, className):
        if className == 1:
            self.Health=1000
            self.AttkMax=140
            self.BlckMax=30
            self.Mana=30
            self.ClassName=WarriorClasses(1).name
        elif className == 2:
            self.Health=1200
            self.AttkMax=100
            self.BlckMax=60
            self.Mana=20
            self.ClassName=WarriorClasses(2).name
        elif className == 3:
            self.Health=700
            self.AttkMax=200
            self.BlckMax=20
            self.Mana=50
            self.ClassName=WarriorClasses(3).name


class WarriorClasses(Enum):
    BERSERKER=1
    TANK=2
    WIZARD=3


def setup(bot):
    bot.add_cog(Duel(bot))
