import discord
from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType
from YTDLSource import YTDLSource
from YTDLSource import PlaylistHelper
from PlayList import PlayList
import random
import time
import os
import datetime
import json
import asyncio

bot = commands.Bot(command_prefix='.')
Discord_Bot_Dir = str('.\\')

marshDiscordId = "224618877626089483"
jackDiscordId = "276462585690193921"

@bot.event
async def on_ready():
    activity = discord.Activity(type=discord.ActivityType.listening, name=".help")
    await bot.change_presence(activity=activity)
    print(f'Logged on and ready to use!')

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        pass

@bot.command(brief='In Progress 😊')
async def cd(ctx):
    Tday = datetime.date.today()
    f_date = datetime.date(2020, 8, 10)
    delta = f_date - Tday
    if ctx.author.id == marshDiscordId:
        await ctx.channel.send(delta)
    elif ctx.author.id == 704589853974855770:
        await ctx.channel.send(delta)

@bot.command(pass_context=True, aliases=["p", "sing"])
async def play(ctx, *, url):
    if PlaylistHelper.checkIfYoutubePlayList(url):
        urls = YTDLSource.get_playlist_info(url)['urls']
        embed = discord.Embed(
            title="Queued " + str(len(urls)) + " Songs",
            description='Playing Song!',
            colour = discord.Colour.red()
        )
        await ctx.channel.send(embed=embed)

        if not ctx.voice_client.is_playing():
            try:
                player = await YTDLSource.from_url(urls.pop(0), stream=True)
                if player is not None:
                    if ctx.voice_client.is_playing():
                        ctx.voice_client.stop()
                    ctx.voice_client.play(player, after=lambda e: check_queue(ctx))
                    embed = discord.Embed(
                        title = 'Playing: ' + player.title,
                        description='Playing Song!',
                        colour = discord.Colour.red()
                    )
                    await ctx.channel.send(embed=embed)
            except Exception as err:
                embed = discord.Embed(
                    title = 'ERROR: {0}'.format(err),
                    description='Playing Song!',
                    colour = discord.Colour.dark_blue()
                )
                await ctx.channel.send(embed=embed)

        for entry in urls:
            PlayList.queue(entry)
    else:
        player = await YTDLSource.from_url(url, stream=True)
        if ctx.voice_client.is_playing():
            PlayList.queue(url)
        else:
            try:
                if player is not None:
                    if ctx.voice_client.is_playing():
                        ctx.voice_client.stop()
                    ctx.voice_client.play(player, after=lambda e: check_queue(ctx))
                    embed = discord.Embed(
                        title = 'Playing: ' + player.title,
                        description='Playing Song!',
                        colour = discord.Colour.red()
                    )
                    await ctx.channel.send(embed=embed)
            except Exception as err:
                embed = discord.Embed(
                    title = 'ERROR: {0}'.format(err),
                    description='Playing Song!',
                    colour = discord.Colour.dark_blue()
                )
                await ctx.channel.send(embed=embed)

@bot.command(pass_context=True, aliases=["l", "disconnect"])
async def leave(ctx):
    server = ctx.message.guild.voice_client
    await server.disconnect()


@bot.command(pass_context=True, aliases=["r", "random"])
async def shuffle(ctx):
    PlayList.shuffle = not PlayList.shuffle


@bot.command()
async def skip(ctx):
    await play_next_song(ctx)


@play.error
async def play_error(ctx, error):
    await ctx.channel.send('Cant play the song!')

def check_queue(ctx):
    if not ctx.voice_client.is_playing():
        asyncio.run(play_next_song(ctx))
    else:
        pass

async def play_next_song(ctx):
    try:
        player = await PlayList.get_next_song()
        if player is not None:
            if ctx.voice_client.is_playing():
                ctx.voice_client.stop()
            ctx.voice_client.play(player, after=lambda e: check_queue(ctx))
            embed = discord.Embed(
                title = 'Playing: ' + player.title,
                description='Playing Song!',
                colour = discord.Colour.red()
            )
            await ctx.channel.send(embed=embed)
    except Exception as err:
        embed = discord.Embed(
            title = 'ERROR: {0}'.format(err),
            description='Playing Song!',
            colour = discord.Colour.dark_blue()
        )
        await ctx.send(embed=embed)

@play.before_invoke
async def ensure_voice(ctx):
    if ctx.voice_client is None:
        if ctx.author.voice:
            await ctx.author.voice.channel.connect()
        else:
            await ctx.channel.send("You are not connected to a voice channel.")
            raise commands.CommandError("Author not connected to a voice channel.")

@bot.command()
async def summon(ctx):
    await ctx.author.voice.channel.connect()

@bot.command(aliases=['8ball'], brief='AKA 8ball, Ask the bot a question that you dont want the answer to.')
async def eightball(ctx,*,question):
    responses = ['It is certain.',
                'It is decidedly so.',
                'Without a doubt.',
                'Yes - definitely.',
                'You may rely on it.',
                'As I see it, yes.',
                'Most likely.',
                'Outlook good.',
                'Yes.',
                'Signs point to yes.',
                'Reply hazy, try again.',
                'Ask again later.',
                'Better not tell you now.',
                'Cannot predict now.',
                'Concentrate and ask again.',
                "Don't count on it.",
                'My reply is no.',
                'My sources say no.',
                'Outlook not so good.',
                'Very doubtful.']
    await ctx.channel.send(f'Question: {question}\nAnswer: {random.choice(responses)}')

@bot.command(brief='Clears messages within the current channel.')
@commands.has_permissions(manage_messages=True)
async def clear(ctx,amount):
    amount = int(amount)
    if amount <= 100:
        await ctx.channel.purge(limit=amount + 1)
    else:
        await ctx.channel.send('Cannot delete more than 100 messages at a time!')

@clear.error
async def clear_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
      await ctx.channel.send('Please put an amount to clear.')

@bot.command(aliases=['penis','pipa','pene'], brief='Ego problems? No problem I can help you with that.')
async def pp(ctx, member : discord.member):
    i = 0
    PP_Size = '='
    while (i <= random.randint(1,18)):
        PP_Size = PP_Size + '='
        i += 1
    embed = discord.Embed(
        title = 'AYE DAWG NICE PEEPEE!',
        description = str(member.name) + '\'s penis size is ' + str(len(PP_Size)) + 'in 😘\n8' + PP_Size + 'D',
        colour = discord.Colour.magenta()
    )
    await ctx.channel.send(embed=embed)

@pp.error
async def pp_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        self_message = str(ctx.author)
        author = self_message.split('#')
        i = 0
        PP_Size = '='
        while (i <= random.randint(1,18)):
            PP_Size = PP_Size + '='
            i += 1
        embed = discord.Embed(
            title = 'AYE DAWG NICE PEEPEE!',
            description = str(author[0]) + '\'s penis size is ' + str(len(PP_Size)) + 'in 😘\n8' + PP_Size + 'D',
            colour = discord.Colour.magenta()
        )
        await ctx.channel.send(embed=embed)

@bot.command(aliases=['insult','burn'], brief='Insult someone until they cry')
async def roast(ctx, member : discord.Member):
    if str(bot.user.id) == str(member.id):
        replys = ['Simmer down buddy 🔫',
                'You dare challenge thy master?! 💪',
                'OK homie relax.. 💩',
                'You aint even worth it dawg 🤏',
                'HA! Good one. 😂',
                'You done yet? Pussy.',
                'Fuck off!!'
        ]
        await ctx.channel.send(f'{random.choice(replys)}')
    else:
        self_message = str(ctx.author)
        author = self_message.split('#')
        i = 0
        file = open(Discord_Bot_Dir + 'insults.txt','rt')
        num_lines = sum(1 for line in file)
        this_num = random.randint(1,int(f'{num_lines}'))
        file = open(Discord_Bot_Dir + 'insults.txt','rt')
        for insultline in file:
            i += 1
            if i == this_num:
                this_line = insultline
                break
        embed = discord.Embed(
            title = 'HOMIE INSULTS! 🔥',
            description = str(author[0]) + ' says: ay ' + str(member.name) + ', ' + this_line,
            colour = discord.Colour.orange()
        )
        await ctx.channel.send(embed=embed)
        file.close()
        this_line = None

@roast.error
async def roast_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        self_message = str(ctx.author)
        author = self_message.split('#')
        i = 0
        file = open(Discord_Bot_Dir + 'insults.txt','rt')
        num_lines = sum(1 for line in file)
        this_num = random.randint(1,int(f'{num_lines}'))
        file = open(Discord_Bot_Dir + 'insults.txt','rt')
        for insultline in file:
            i += 1
            if i == this_num:
                this_line = insultline
                break
        embed = discord.Embed(
            title = 'HOMIE INSULTS! 🔥',
            description = 'Homie Bot says: ay ' + str(author[0]) + ', ' + this_line,
            colour = discord.Colour.red()
        )
        await ctx.channel.send(embed=embed)
        file.close()
        this_line = None

@bot.command(brief='Wanna hit on someone? Let me be your wingman!')
async def pickup(ctx, member : discord.Member):
    self_message = str(ctx.author)
    author = self_message.split('#')
    i = 0
    file = open(Discord_Bot_Dir + 'pickup.txt','rt')
    num_lines = sum(1 for line in file)
    this_num = random.randint(1,int(f'{num_lines}'))
    file = open(Discord_Bot_Dir + 'pickup.txt','rt')
    for pickupline in file:
        i += 1
        if i == this_num:
            this_line = pickupline
            break
    embed = discord.Embed(
        title = 'HOMIE PICKUPS! 🌈',
        description = str(author[0]) + ' says: ay ' + str(member.name) + ', ' + this_line,
        colour = discord.Colour.orange()
    )
    await ctx.channel.send(embed=embed)
    file.close()
    this_line = None

@pickup.error
async def pickup_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        self_message = str(ctx.author)
        author = self_message.split('#')
        i = 0
        file = open(Discord_Bot_Dir + 'pickup.txt','rt')
        num_lines = sum(1 for line in file)
        this_num = random.randint(1,int(f'{num_lines}'))
        file = open(Discord_Bot_Dir + 'pickup.txt','rt')
        for pickupline in file:
            i += 1
            if i == this_num:
                this_line = pickupline
                break
        embed = discord.Embed(
            title = 'HOMIE PICKUPS! 🌈',
            description = 'Homie Bot says: ay ' + str(author[0]) + ', ' + this_line,
            colour = discord.Colour.orange()
        )
        await ctx.channel.send(embed=embed)
        file.close()
        this_line = None

@bot.command(aliases=['duel'], brief='Fight someone on this server!')
@commands.max_concurrency(1,per=BucketType.default,wait=True)
async def fight(ctx, member : discord.Member):
    duel_author = str(ctx.author)
    duelers_id = str(ctx.author.id)
    duel_authors_name = duel_author.split('#')
    challenge_member = str(member.name)
    challenge_member_id = str(member.id)
    bot_name = str(bot.user)
    bot_username = bot_name.split('#')

    hit_response = [    'cRaZyy',
                        'pOwerful',
                        'DEADLY',
                        'dangerous',
                        'deathly',
                        'l33t',
                        'amazing'
    ]
    
    #fighting yourself? Loser.
    if str(duelers_id) == str(challenge_member_id):
        replys = [  'Dumbass.. You cant challenge yourself! 🤡',
                    'LOL! IDIOT! 🤣',
                    'Homie... Chillax. Stop beefing with yo self 👊',
                    'You good bro? 😥',
                    'REEEEELLLAAAAXXXXXXXXX 😬',
                    'Its gonna be okay 😔'
        ]
        await ctx.channel.send(f'{random.choice(replys)}')

    #fighting the bot? KEKW
    elif str(challenge_member) == str(bot_username[0]):
        replys = [  'Simmer down buddy 🔫',
                    'You dare challenge thy master?! 💪',
                    'OK homie relax.. 💩',
                    'You aint even worth it dawg 🤏',
                    'You a one pump chump anyway 🤡',
                    'HA! Good one. 😂',
                    'You done yet? Pussy.'
        ]
        await ctx.channel.send(f'{random.choice(replys)}')

    #fighting other users
    else:
        embed = discord.Embed(
            title = '⚔️ ' + duel_authors_name[0] + ' has challenged ' + challenge_member + ' to a fight!',
            description=member.mention + ', what would like to do? `punch`,`defend`, or `end`?\nType your choice out in chat as it is displayed!',
            colour = discord.Colour.red()
        )
        await ctx.channel.send(embed=embed)
        
        fight_turn = 0
        challenge_member_health = int(100)
        duelers_health = int(100)
        punch_damage = int(random.randint(1,100))
        def inner_check(message):
            return message.content == 'punch' or message.content == 'defend' or message.content == 'end'

        while challenge_member_health != 0 or duelers_health != 0:
            try:
                msg = await bot.wait_for('message', check=inner_check, timeout=30.0)
            except asyncio.TimeoutError:
                if (fight_turn % 2) == 0:
                    await ctx.channel.send('Nice fight idiots.. **' + duel_authors_name[0] + '** wins!')
                    break
                else:
                    await ctx.channel.send('Nice fight idiots.. **' + challenge_member + '** wins!')
                    break
            if str(msg.content) == 'punch' and str(msg.author.id) == challenge_member_id and (fight_turn % 2) == 0:
                fight_turn += 1
                
                #jack always punches for 100 damage cuz he is 4WeirdBuff
                if str(msg.author.id) == jackDiscordId:
                    punch_damage = 100
                duelers_health -= punch_damage
                await ctx.channel.send('**' + challenge_member + '** lands a ' + f'{random.choice(hit_response)}' + ' hit on **' + duel_authors_name[0] + '** dealing `' + f'{punch_damage}' + '` damage!\n**' + duel_authors_name[0] + '** is left with `' + f'{duelers_health}' + '` health!')
                               
                if duelers_health <= 0:
                    embed = discord.Embed(
                        title = 'STOP! STOP! STOP! THE FIGHT IS OVER!!!',
                        description = '**' + f'{challenge_member}' + '** wins with just `' + f'{challenge_member_health}' + ' HP` left!',
                        colour = discord.Colour.teal()
                    )
                    await ctx.channel.send(embed=embed)
                    break
                else:
                    await ctx.channel.send(ctx.author.mention + ', what would like to do? `punch`,`defend`, or `end`?\nType your choice out in chat as it is displayed!')
                    punch_damage = int(random.randint(1,int(f'{challenge_member_health}'))) 
            elif str(msg.content) == 'punch' and str(msg.author.id) == duelers_id and (fight_turn % 2) != 0:
                fight_turn += 1

                #jack always punches for 100 damage cuz he is 4WeirdBuff
                if str(msg.author.id) == jackDiscordId:
                    punch_damage = 100
                challenge_member_health -= punch_damage
                await ctx.channel.send('**' + duel_authors_name[0] + '** lands a ' + f'{random.choice(hit_response)}' + ' hit on **' + challenge_member + '** dealing `' + f'{punch_damage}' + '` damage!\n**' + challenge_member + '** is left with `' + f'{challenge_member_health}' + '` health!')
                           
                if challenge_member_health == 0:
                    embed = discord.Embed(
                        title = 'STOP! STOP! STOP! THE FIGHT IS OVER!!!',
                        description = '**' + f'{duel_authors_name[0]}' + '** wins with just `' + f'{duelers_health}' + ' HP` left!',
                        colour = discord.Colour.teal()
                    )
                    await ctx.channel.send(embed=embed)
                    break
                else:
                    await ctx.channel.send(member.mention + ', what would like to do? `punch`,`defend`, or `end`?\nType your choice out in chat as it is displayed!')
                    punch_damage = int(random.randint(1,int(f'{duelers_health}')))  
            elif str(msg.content) == 'defend' and str(msg.author.id) == duelers_id and (fight_turn % 2) != 0:
                fight_turn += 1
                await defenseResponse(ctx, duel_authors_name[0], member.mention)
            elif str(msg.content) == 'defend' and str(msg.author.id) == challenge_member_id and (fight_turn % 2) == 0:
                fight_turn += 1
                await defenseResponse(ctx, challenge_member, ctx.author.mention)
            elif str(msg.content) == 'end' and str(msg.author.id) == duelers_id and (fight_turn % 2) != 0:
                await ctx.channel.send(duel_authors_name[0] + ' has ended the fight. What a wimp.')
                break
            elif str(msg.content) == 'end' and str(msg.author.id) == challenge_member_id and (fight_turn % 2) == 0:
                await ctx.channel.send(challenge_member + ' has ended the fight. What a wimp.')
                break

async def defenseResponse(ctx, person, mentionedUser):
    print("im in defenseResponse()")
    defence_points = int(random.randint(1,10))
    print(mentionedUser)
    await ctx.channel.send('**' + f'{person}' + '** boosted their defense by `' + f'{defence_points}' + '` points!')
    await ctx.channel.send(mentionedUser + ', what would like to do? `punch`,`defend`, or `end`?\nType your choice out in chat as it is displayed!')

@fight.error
async def fight_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.channel.send('Who you tryna fight, the air?! Choose someone to fight you pleb! 🤡')

@bot.command(brief='Enlarge and view your profile picture or another member')
async def av(ctx, member : discord.Member):
    embed = discord.Embed(
        title = str(member.name),
        description = 'Avatar',
        colour = discord.Colour.light_grey()
    )
    embed.set_image(url=member.avatar_url)
    await ctx.channel.send(embed=embed)

@av.error
async def av_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        embed = discord.Embed(
        title = str(ctx.author),
        description = 'Avatar',
        colour = discord.Colour.light_grey()
    )
    embed.set_image(url=ctx.author.avatar_url)
    await ctx.channel.send(embed=embed)

@bot.command(brief='Bite someone or yourself')
async def bite(ctx, member : discord.Member):
    self_message = str(ctx.author)
    author = self_message.split('#')
    i = 0
    file = open(Discord_Bot_Dir + 'bite.txt','rt')
    num_lines = sum(1 for line in file)
    this_num = random.randint(1,int(f'{num_lines}'))
    file = open(Discord_Bot_Dir + 'bite.txt','rt')
    for gifline in file:
        i += 1
        if i == this_num:
            this_line = gifline
            break
    embed = discord.Embed(
        title = str(author[0]) + ' bites ' + str(member.name),
        colour = discord.Colour.from_rgb(0,0,0)
    )
    embed.set_image(url=this_line)
    await ctx.channel.send(embed=embed)
    file.close()
    this_line = None
    num_lines = None

@bite.error
async def bite_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        self_message = str(ctx.author)
        author = self_message.split('#')
        i = 0
        file = open(Discord_Bot_Dir + 'bite.txt','rt')
        num_lines = sum(1 for line in file)
        this_num = random.randint(1,int(f'{num_lines}'))
        file = open(Discord_Bot_Dir + 'bite.txt','rt')
        for gifline in file:
            i += 1
            if i == this_num:
                this_line = gifline
                break
        embed = discord.Embed(
            title = 'Homie Bot bites ' + str(author[0]),
            colour = discord.Colour.from_rgb(0,0,0)
        )
        embed.set_image(url=this_line)
        await ctx.channel.send(embed=embed)
        file.close()
        this_line = None
        num_lines = None

@bot.command(brief='Cuddle someone or yourself')
async def cuddle(ctx, member : discord.Member):
    self_message = str(ctx.author)
    author = self_message.split('#')
    i = 0
    file = open(Discord_Bot_Dir + 'cuddle.txt','rt')
    num_lines = sum(1 for line in file)
    this_num = random.randint(1,int(f'{num_lines}'))
    file = open(Discord_Bot_Dir + 'cuddle.txt','rt')
    for gifline in file:
        i += 1
        if i == this_num:
            this_line = gifline
            break
    embed = discord.Embed(
        title = str(author[0]) + ' cuddles ' + str(member.name) + ' 🤗',
        colour = discord.Colour.from_rgb(0,0,0)
    )
    embed.set_image(url=this_line)
    await ctx.channel.send(embed=embed)
    file.close()
    this_line = None
    num_lines = None

@cuddle.error
async def cuddle_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        self_message = str(ctx.author)
        author = self_message.split('#')
        i = 0
        file = open(Discord_Bot_Dir + 'cuddle.txt','rt')
        num_lines = sum(1 for line in file)
        this_num = random.randint(1,int(f'{num_lines}'))
        file = open(Discord_Bot_Dir + 'cuddle.txt','rt')
        for gifline in file:
            i += 1
            if i == this_num:
                this_line = gifline
                break
        embed = discord.Embed(
            title = 'Homie Bot cuddles ' + str(author[0]) + ' 🤗',
            colour = discord.Colour.from_rgb(0,0,0)
        )
        embed.set_image(url=this_line)
        await ctx.channel.send(embed=embed)
        file.close()
        this_line = None
        num_lines = None

@bot.command(brief='Hug someone or yourself')
async def hug(ctx, member : discord.Member):
    self_message = str(ctx.author)
    author = self_message.split('#')
    i = 0
    file = open(Discord_Bot_Dir + 'hug.txt','rt')
    num_lines = sum(1 for line in file)
    this_num = random.randint(1,int(f'{num_lines}'))
    file = open(Discord_Bot_Dir + 'hug.txt','rt')
    for gifline in file:
        i += 1
        if i == this_num:
            this_line = gifline
            break
    embed = discord.Embed(
        title = str(author[0]) + ' hugs ' + str(member.name) + ' 🤗',
        colour = discord.Colour.from_rgb(0,0,0)
    )
    embed.set_image(url=this_line)
    await ctx.channel.send(embed=embed)
    file.close()
    this_line = None
    num_lines = None

@hug.error
async def hug_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        self_message = str(ctx.author)
        author = self_message.split('#')
        i = 0
        file = open(Discord_Bot_Dir + 'hug.txt','rt')
        num_lines = sum(1 for line in file)
        this_num = random.randint(1,int(f'{num_lines}'))
        file = open(Discord_Bot_Dir + 'hug.txt','rt')
        for gifline in file:
            i += 1
            if i == this_num:
                this_line = gifline
                break
        embed = discord.Embed(
            title = 'Homie Bot hugs ' + str(author[0]) + ' 🤗',
            colour = discord.Colour.from_rgb(0,0,0)
        )
        embed.set_image(url=this_line)
        await ctx.channel.send(embed=embed)
        file.close()
        this_line = None
        num_lines = None

@bot.command(brief='Kiss someone or yourself')
async def kiss(ctx, member : discord.Member):
    self_message = str(ctx.author)
    author = self_message.split('#')
    i = 0
    file = open(Discord_Bot_Dir + 'kiss.txt','rt')
    num_lines = sum(1 for line in file)
    this_num = random.randint(1,int(f'{num_lines}'))
    file = open(Discord_Bot_Dir + 'kiss.txt','rt')
    for gifline in file:
        i += 1
        if i == this_num:
            this_line = gifline
            break
    embed = discord.Embed(
        title = str(author[0]) + ' kisses ' + str(member.name) + ' 💋',
        colour = discord.Colour.from_rgb(0,0,0)
    )
    embed.set_image(url=this_line)
    await ctx.channel.send(embed=embed)
    file.close()
    this_line = None
    num_lines = None

@kiss.error
async def kiss_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        self_message = str(ctx.author)
        author = self_message.split('#')
        i = 0
        file = open(Discord_Bot_Dir + 'kiss.txt','rt')
        num_lines = sum(1 for line in file)
        this_num = random.randint(1,int(f'{num_lines}'))
        file = open(Discord_Bot_Dir + 'kiss.txt','rt')
        for gifline in file:
            i += 1
            if i == this_num:
                this_line = gifline
                break
        embed = discord.Embed(
            title = 'Homie Bot kisses ' + str(author[0]) + ' 💋',
            colour = discord.Colour.from_rgb(0,0,0)
        )
        embed.set_image(url=this_line)
        await ctx.channel.send(embed=embed)
        file.close()
        this_line = None
        num_lines = None

@bot.command(brief='Slap someone or yourself')
async def slap(ctx, member : discord.Member):
    self_message = str(ctx.author)
    author = self_message.split('#')
    i = 0
    file = open(Discord_Bot_Dir + 'slap.txt','rt')
    num_lines = sum(1 for line in file)
    this_num = random.randint(1,int(f'{num_lines}'))
    file = open(Discord_Bot_Dir + 'slap.txt','rt')
    for gifline in file:
        i += 1
        if i == this_num:
            this_line = gifline
            break
    embed = discord.Embed(
        title = str(author[0]) + ' slaps ' + str(member.name) + ' 😡',
        colour = discord.Colour.from_rgb(0,0,0)
    )
    embed.set_image(url=this_line)
    await ctx.channel.send(embed=embed)
    file.close()
    this_line = None
    num_lines = None

@slap.error
async def slap_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        self_message = str(ctx.author)
        author = self_message.split('#')
        i = 0
        file = open(Discord_Bot_Dir + 'slap.txt','rt')
        num_lines = sum(1 for line in file)
        this_num = random.randint(1,int(f'{num_lines}'))
        file = open(Discord_Bot_Dir + 'slap.txt','rt')
        for gifline in file:
            i += 1
            if i == this_num:
                this_line = gifline
                break
        embed = discord.Embed(
            title = 'Homie Bot slaps ' + str(author[0]) + ' 😡',
            colour = discord.Colour.from_rgb(0,0,0)
        )
        embed.set_image(url=this_line)
        await ctx.channel.send(embed=embed)
        file.close()
        this_line = None
        num_lines = None

file = open(Discord_Bot_Dir + 'token.txt','rt')
bot.run(str(file.read()))