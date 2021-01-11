import discord
from discord.ext import commands, tasks
import requests
from bs4 import BeautifulSoup
from datetime import datetime

URL = "https://www.daydeal.ch/"


async def availableBarCreator(available):
    bar = "["
    if int(available) == 50:
        bar += ("l" * int(available)) + "]"
    else:
        bar += ("l" * int(available)) + "||" + ("l" * (50 - int(available))) + "||]"
    bar += " (" + str(int(available) * 2) + "%)"
    return bar


class Daydeal(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.channel = None
        self.mention_role = None
        self.endTime = None

    @commands.command()
    @commands.has_permissions(manage_channels=True)
    async def setupDaydeal(self, ctx, channel: discord.TextChannel, mention_role: discord.Role):
        self.channel = channel
        self.mention_role = mention_role
        if self.channel and self.mention_role:
            await ctx.invoke(self.bot.get_command('deal'))
            await ctx.channel.send("Setup successful.")
            await self.daydeal_task.start(ctx)

    @setupDaydeal.error
    async def setupDaydeal_error(self, ctx, error):
        await ctx.channel.send("Error. Please use command like this: ```,setupDaydeal #channel @role``` Error cause: " + str(error))

    @commands.command()
    @commands.has_permissions(manage_channels=True)
    async def stopDaydeal(self, ctx):
        await self.daydeal_task.cancel()
        await ctx.channel.send("Daydeal stopped.")

    @tasks.loop(seconds=180.0)
    async def daydeal_task(self, ctx):
        if datetime.now() >= self.endTime:
            await ctx.invoke(self.bot.get_command('deal'))

    @commands.command()
    async def deal(self, ctx):
        # Web Scraping
        page = requests.get(URL)
        soup = BeautifulSoup(page.content, 'html.parser')
        self.endTime = datetime.strptime(soup.find('div', class_='product-bar__offer-ends').findChild()['data-next-deal'], '%Y-%m-%d %H:%M:%S')
        product_description = soup.find('section', class_='product-description')
        title1 = product_description.find('h1', class_='product-description__title1').text
        title2 = product_description.find('h2', class_='product-description__title2').text
        description_details = product_description.find('ul', class_='product-description__list').findChildren()
        product_img = soup.find('img', class_='product-img-main-pic')['src']
        new_price = soup.find('h2', class_='product-pricing__prices-new-price').text
        old_price = soup.find('span', class_='js-old-price')
        if old_price is not None:
            old_price = old_price.text
        else:
            old_price = ""
        available = int(soup.find('strong', class_='product-progress__availability').text.strip('%')) / 2
        ends_in = self.endTime - datetime.now().replace(microsecond=0)
        description_str = ""
        for element in description_details:
            description_str += "• " + element.text + "\n"

        # Create embed message
        embed = discord.Embed(title=title2, description=description_str, url=URL, colour=0x23b40c)
        embed.set_thumbnail(url="https://static.daydeal.ch/2.17.10/images/logo-top.png")
        embed.set_image(url=product_img)
        embed.set_author(name='Today\'s deal: ' + title1)
        embed.add_field(name="Price", value="Now: " + new_price + ", Old: " + old_price, inline=False)
        embed.add_field(name="Available", value=str(await availableBarCreator(available)), inline=False)
        embed.add_field(name="Ends in", value=str(ends_in), inline=False)
        if self.channel is None:
            self.channel = ctx.channel
        await self.channel.send(embed=embed)
        if self.mention_role is not None:
            await self.channel.send(self.mention_role.mention)

    @deal.error
    async def deal_error(self, ctx, error):
        await ctx.channel.send('error:  ' + str(error))


def setup(bot):
    bot.add_cog(Daydeal(bot))
