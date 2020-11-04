import discord
import random
from discord.ext import commands
from pathlib import Path
import requests
from bs4 import BeautifulSoup
from datetime import date, time, datetime

Discord_Bot_Dir = Path("./")
linksPath = Path(Discord_Bot_Dir/"links/")

async def availableBarCreator():
    "["+("l"*int(available))+"||"+("l‏‎‎"*(50-int(available)))+"||] ("+str(available)+"%)"

class Daydeal(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def deal(self, ctx):
        URL = "https://www.daydeal.ch/"
        page = requests.get(URL)
        soup = BeautifulSoup(page.content, 'html.parser')
        product_description = soup.find('section', class_='product-description')
        title1 = product_description.find('h1', class_='product-description__title1').text
        title2 = product_description.find('h2', class_='product-description__title2').text
        description_details = product_description.find('ul', class_='product-description__list').findChildren()
        product_img = soup.find('img', class_='product-img-main-pic')['src']
        newPrice = soup.find('h2', class_='product-pricing__prices-new-price').text
        oldPrice = soup.find('span', class_='js-old-price').text
        #available = 50/100*int(soup.find('strong', class_='product-progress__availability').text.strip('%'))
        available = 50
        endsOn = datetime.strptime(soup.find('div', class_='product-bar__offer-ends').findChild()['data-next-deal'], '%Y-%m-%d %H:%M:%S')
        endsIn = endsOn - datetime.now().replace(microsecond=0)
        
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
        embed.add_field(name="Available", value="", inline=False)
        embed.add_field(name="Ends in", value=endsIn, inline=False)
        await ctx.channel.send(embed=embed)

    @deal.error
    async def deal_error(self, ctx, error):
        await ctx.channel.send('error:  '+str(error))

def setup(bot):
    bot.add_cog(Daydeal(bot))

