import discord
import random
from discord.ext import commands
from pathlib import Path
import requests
from bs4 import BeautifulSoup

Discord_Bot_Dir = Path("./")
linksPath = Path(Discord_Bot_Dir/"links/")

class Daydeal(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def deal(self, ctx):
        URL = "https://www.daydeal.ch/"
        page = requests.get(URL)
        soup = BeautifulSoup(page.content, 'html.parser')
        product_description = soup.find('section', class_='product-description')
        product_img = soup.find('div', class_='product-img').find('img', class_='product-img-main-pic')['src']
        title1 = product_description.find('h1', class_='product-description__title1').text
        title2 = product_description.find('h2', class_='product-description__title2').text
        description_details = product_description.find('ul', class_='product-description__list').findChildren()
        description_str = ""
        for element in description_details:
            description_str += "• "+element.text+"\n"

        embed = discord.Embed(
            title = title2,
            colour = discord.Colour.from_rgb(35,180,12),
            description = description_str
        )
        embed.set_author(name='Todays deal: ' + title1)
        embed.set_image(url=product_img)
        await ctx.channel.send(embed=embed)

    @deal.error
    async def deal_error(self, ctx, error):
        await ctx.channel.send('Please put an amount to clear. '+error)

def setup(bot):
    bot.add_cog(Daydeal(bot))