import discord
from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType
from enum import Enum
import asyncio
import random


class Duel(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    @commands.command(aliases=['duel'], brief='Fight someone on this server!')
    @commands.max_concurrency(1,per=BucketType.default,wait=True)
    async def fight(self, ctx, member : discord.Member):
        duel_authors_id = ctx.author.id
        duel_authors_name = ctx.author.name
        challenge_member_name = member.name
        challenge_member_id = member.id
        bot_id = self.bot.user.id
        
        #fighting yourself? Loser.
        if duel_authors_id == challenge_member_id:
            replys = ['Dumbass.. You cant challenge yourself! 🤡','LOL! IDIOT! 🤣','Homie... Chillax. Stop beefing with yo self 👊','You good bro? 😥','REEEEELLLAAAAXXXXXXXXX 😬','Its gonna be okay 😔']
            await ctx.channel.send(random.choice(replys))

        #fighting the bot? KEKW
        elif challenge_member_id == bot_id:
            replys = [  'Simmer down buddy 🔫','You dare challenge thy master?! 💪','OK homie relax.. 💩','You aint even worth it dawg 🤏','You a one pump chump anyway 🤡','HA! Good one. 😂','You done yet? Pussy.']
            await ctx.channel.send(random.choice(replys))

        #fighting other users
        else:
            embed = discord.Embed(
                title = '⚔️ ' + duel_authors_name + ' choose your class.',
                description= ctx.author.mention+'what class do you want to be? `berserker`, `tank` or `wizard`?',
                colour = discord.Colour.red()
            )
            await ctx.channel.send(embed=embed)

            warrior1 = await self.createWarrior(ctx, ctx.author)

            embed = discord.Embed(
                title = '⚔️ ' + duel_authors_name + ' has challenged ' + challenge_member_name + ' to a fight!',
                description = duel_authors_name + ' chose class ' + warrior1.ClassName + '. ' + member.mention + ', what is your class of choice? `berserker`,`tank`, or `wizard`?\nType your choice out in chat as it is displayed!',
                colour = discord.Colour.red()
            )
            await ctx.channel.send(embed=embed)

            warrior2 = await self.createWarrior(ctx, member)
            
            await ctx.channel.send(member.mention + ', what would like to do? `punch`,`defend`, or `end`?\nType your choice out in chat as it is displayed!')

            fight_turn = 0
            def checkAction(message):
                return message.content == 'punch' or message.content == 'defend' or message.content == 'end'

            while warrior1.Health > 0 and warrior2.Health > 0:
                try:
                    msg = await self.bot.wait_for('message', check=checkAction, timeout=30.0)
                    if str(msg.content) == 'punch' and msg.author.id == challenge_member_id and (fight_turn % 2) == 0:
                        fight_turn += 1
                        if await self.getActionResult(warrior2, warrior1, ctx):
                            break
                    elif str(msg.content) == 'punch' and msg.author.id == duel_authors_id and (fight_turn % 2) != 0:
                        fight_turn += 1
                        if await self.getActionResult(warrior1, warrior2, ctx):
                            break
                    elif str(msg.content) == 'defend' and msg.author.id == challenge_member_id and (fight_turn % 2) == 0:
                        fight_turn += 1
                        await self.defenseResponse(ctx, challenge_member_name, ctx.author.mention)
                    elif str(msg.content) == 'defend' and msg.author.id == duel_authors_id and (fight_turn % 2) != 0:
                        fight_turn += 1
                        await self.defenseResponse(ctx, duel_authors_name, member.mention)
                    elif str(msg.content) == 'end' and msg.author.id == challenge_member_id and (fight_turn % 2) == 0:
                        await ctx.channel.send(challenge_member_name + ' has ended the fight. What a wimp.')
                        break   
                    elif str(msg.content) == 'end' and msg.author.id == duel_authors_id and (fight_turn % 2) != 0:
                        await ctx.channel.send(duel_authors_name + ' has ended the fight. What a wimp.')
                        break
                except asyncio.TimeoutError:
                    if (fight_turn % 2) == 0:
                        await ctx.channel.send('Nice fight idiots.. **' + duel_authors_name + '** wins!')
                        break
                    else:
                        await ctx.channel.send('Nice fight idiots.. **' + challenge_member_name + '** wins!')
                        break

    def checkClassChooser(self, author):
        def inner_check(message):
            return (message.content == 'berserker' or message.content == 'tank' or message.content == 'wizard') and message.author == author
        return inner_check

    async def createWarrior(self, ctx, user):
        try:
            msgClass = await self.bot.wait_for('message', check=self.checkClassChooser(user), timeout=30.0)
            warrior = Warrior(msgClass.author)
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
        attackDamage = random.randrange(0,warrior1.AttkMax) + 20
        counterDamage = random.randrange(0,warrior2.AttkMax)

        warrior2.Health -= attackDamage
        warrior1.Health -= counterDamage

        hit_response = ['cRaZyy','pOwerful','DEADLY','dangerous','deathly','l33t','amazing']

        await ctx.channel.send('**' + warrior1.user.name + '** lands a ' + random.choice(hit_response) + ' hit on **' + warrior2.user.name + '** dealing `' + str(attackDamage) + '` damage!\n**' + warrior2.user.name + '** did ' + str(counterDamage) + ' counter damage!\n' + warrior2.user.name + '  is left with `' + str(warrior2.Health) + '` health!\n' + warrior1.user.name + ' is left with `' + str(warrior1.Health) + '` health!')
        if warrior2.Health < 0:
            winEmbedMessage = discord.Embed(
                            title = 'STOP! STOP! STOP! THE FIGHT IS OVER!!!',
                            description = '**' + warrior1.user.name + '** wins with just `' + str(warrior1.Health) + ' HP` left!',
                            colour = discord.Colour.teal()
            )
            await ctx.channel.send(embed=winEmbedMessage)
            return True
        else:
            await ctx.channel.send(warrior2.user.mention + ', what would like to do? `punch`,`defend`, or `end`?\nType your choice out in chat as it is displayed!')
            return False


    async def defenseResponse(self, ctx, person, mentionedUser):
        defence_points = int(random.randint(1,10))
        await ctx.channel.send('**' + person + '** boosted their defense by `' + str(defence_points) + '` points!')
        await ctx.channel.send(mentionedUser + ', what would like to do? `punch`,`defend`, or `end`?\nType your choice out in chat as it is displayed!')

    @fight.error
    async def fight_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.channel.send('Who you tryna fight, the air?! Choose someone to fight you pleb! 🤡')

class Warrior:
    def __init__(self, user, health=1, attkMax=1, blckMax=1, mana=1, className=1):
        self.user = user
        self.Health = health
        self.AttkMax = attkMax
        self.BlckMax = blckMax
        self.Mana = mana
        self.ClassName = className

    def chooseClass(self, className):
        if className == 1:
            self.Health = 1000
            self.AttkMax = 140
            self.BlckMax = 30
            self.Mana = 30
            self.ClassName = WarriorClasses(1).name
        elif className == 2:
            self.Health = 1200
            self.AttkMax = 100
            self.BlckMax = 60
            self.Mana = 20
            self.ClassName = WarriorClasses(2).name
        elif className == 3:
            self.Health = 700
            self.AttkMax = 200
            self.BlckMax = 20
            self.Mana = 50
            self.ClassName = WarriorClasses(3).name

class WarriorClasses(Enum):
    BERSERKER = 1
    TANK = 2
    WIZARD = 3

def setup(bot):
    bot.add_cog(Duel(bot))