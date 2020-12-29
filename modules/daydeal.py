import discord
import random
from discord.ext import commands, tasks
from pathlib import Path
import requests
from bs4 import BeautifulSoup
from datetime import date, time, datetime

Discord_Bot_Dir = Path("./")
linksPath = Path(Discord_Bot_Dir/"links/")

URL = "https://www.daydeal.ch/"
page = requests.get(URL)
soup = BeautifulSoup(page.content, 'html.parser')

async def availableBarCreator(available):
    bar = "["
    if int(available) == 50:
        bar += ("l"*int(available))+"]"
    else:
        bar += ("l"*int(available))+"||"+("l‏‎‎"*(50-int(available)))+"||]"
    bar += " ("+str(int(available)*2)+"%)"
    return bar

class Daydeal(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.endTime = datetime.now()

    @commands.command()
    @commands.has_permissions(manage_channels=True)
    async def setupDaydeal(self, ctx, channel : discord.TextChannel, mentionRole : discord.Role):
        self.channel = channel
        self.mentionRole = mentionRole
        if self.channel and self.mentionRole:
            await ctx.invoke(self.bot.get_command('deal'))
            await ctx.channel.send("Setup successful.")
            await self.daydeal_task.start(ctx)
    
    @setupDaydeal.error
    async def setupDaydeal_error(self, ctx, error):
        await ctx.channel.send("Error. Please use command like this: ```,setupDaydeal #channel @role``` Error cause: "+str(error))

    @commands.command()
    async def stopDaydeal(self, ctx):
        await self.daydeal_task.cancel()

    @tasks.loop(seconds=60.0)
    async def daydeal_task(self, ctx):
        current_time = datetime.now()
        self.endTime = datetime.strptime(soup.find('div', class_='product-bar__offer-ends').findChild()['data-next-deal'], '%Y-%m-%d %H:%M:%S')
        if(current_time >= self.endTime):
            await ctx.invoke(self.bot.get_command('deal'))

    @commands.command()
    async def deal(self, ctx):
        product_description = soup.find('section', class_='product-description')
        title1 = product_description.find('h1', class_='product-description__title1').text
        title2 = product_description.find('h2', class_='product-description__title2').text
        description_details = product_description.find('ul', class_='product-description__list').findChildren()
        product_img = soup.find('img', class_='product-img-main-pic')['src']
        newPrice = soup.find('h2', class_='product-pricing__prices-new-price').text
        oldPrice = soup.find('span', class_='js-old-price').text
        available = int(soup.find('strong', class_='product-progress__availability').text.strip('%'))/2
        availableBar = await availableBarCreator(available)
        endsIn = self.endTime - datetime.now().replace(microsecond=0)
        description_str = ""
        for element in description_details:
            description_str += "• "+element.text+"\n"

        embed = discord.Embed(
            title = title2,
            description = description_str,
            url="https://www.daydeal.ch/",
            colour = discord.Colour.from_rgb(35,180,12)
        )
        embed.set_thumbnail(url="https://static.daydeal.ch/2.17.10/images/logo-top.png")
        embed.set_image(url=product_img)
        embed.set_author(name='Todays deal: ' + title1)
        embed.add_field(name="Price", value="Now: "+newPrice+", Old: "+oldPrice, inline=False)
        embed.add_field(name="Available", value=availableBar, inline=False)
        embed.add_field(name="Ends in", value=endsIn, inline=False)
        await self.channel.send(embed=embed)
        await self.channel.send(self.mentionRole.mention)

    @deal.error
    async def deal_error(self, ctx, error):
        await ctx.channel.send('error:  '+str(error))

def setup(bot):
    bot.add_cog(Daydeal(bot))

