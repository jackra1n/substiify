from sqlite3.dbapi2 import Cursor
import discord
from discord import guild, role
from discord.ext import commands, tasks
from discord.ext.commands.core import command
import requests
import sqlite3
from bs4 import BeautifulSoup
from datetime import datetime

URL = "https://www.daydeal.ch/"

class Daydeal(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.channel = None
        self.mention_role = None
        self.endTime = self.getDealEndTime()
        self.db_path = './data/main.sqlite'
        self.daydeal_task.start()

    def getDealEndTime(self):
        page = requests.get(URL)
        soup = BeautifulSoup(page.content, 'html.parser')
        return datetime.strptime(soup.find('div', class_='product-bar__offer-ends').findChild()['data-next-deal'], '%Y-%m-%d %H:%M:%S')

    async def availableBarCreator(self, available):
        toDraw = int(round(available, -1)/10)
        return '<:green_square:820409531573993513>'*toDraw + '<:grey_square:820409550938046514>'*(10-toDraw) + f' `{available}%`'

    async def createDaydealEmbed(self):
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
        embed.add_field(name="Price", value=f'~~`{old_price}`~~ ⟶ `{new_price}`', inline=False)
        embed.add_field(name="Available", value=str(await self.availableBarCreator(available)), inline=False)
        embed.add_field(name="Ends in", value=str(ends_in), inline=False)
        return embed

    @commands.command()
    @commands.has_permissions(manage_channels=True)
    async def setupDaydeal(self, ctx, channel: discord.TextChannel, mention_role: discord.Role):
        self.channel = channel
        self.mention_role = mention_role
        if self.channel is None:
            self.channel = ctx.channel
        if self.channel and self.mention_role:
            db = sqlite3.connect(self.db_path)
            cursor = db.cursor()
            cursor.execute(f"SELECT channel_id FROM daydeal WHERE guild_id = {ctx.guild.id}")
            result = cursor.fetchone()
            if result is None:
                sql = ("INSERT INTO daydeal(guild_id, channel_id, role_id) VALUES (?, ?, ?)")
                val = (str(ctx.guild.id), str(channel.id), str(mention_role.id))
                cursor.execute(sql, val)
                db.commit()
                cursor.close()
                db.close()
                await self.channel.send(content=self.mention_role.mention,embed=await self.createDaydealEmbed())
                await ctx.channel.send(embed=discord.Embed(description='Setup successful', colour=0x23b40c))
            else:
                await ctx.channel.send(embed=discord.Embed(description='Daydeal is already set up', colour=0x23b40c))

    @setupDaydeal.error
    async def setupDaydeal_error(self, ctx, error):
        await ctx.channel.send(str(error))

    @tasks.loop(seconds=60.0)
    async def daydeal_task(self):
        if datetime.now() >= self.endTime:
            db = sqlite3.connect(self.db_path)
            cursor = db.cursor()
            daydealEmbed = await self.createDaydealEmbed()
            for row in cursor.execute(f"SELECT * FROM daydeal"):
                server = self.bot.get_guild(int(row[1]))
                channel = self.bot.get_channel(int(row[2]))
                role = server.get_role(int(row[3]))
                await channel.send(content=role.mention,embed=daydealEmbed)

    @commands.command()
    @commands.has_permissions(manage_channels=True)
    async def stopDaydeal(self, ctx):
        db = sqlite3.connect(self.db_path)
        cursor = db.cursor()
        cursor.execute(f"DELETE FROM daydeal WHERE guild_id = {ctx.guild.id}")
        db.commit()
        cursor.close()
        db.close()
        await ctx.channel.send(embed=discord.Embed(description='Daydeal stopped', colour=0x23b40c))

    @commands.cooldown(4, 10)
    @commands.command()
    async def deal(self, ctx):
        await ctx.channel.send(embed=await self.createDaydealEmbed())

    @deal.error
    async def deal_error(self, ctx, error):
        await ctx.channel.send('error:  ' + str(error))


def setup(bot):
    bot.add_cog(Daydeal(bot))
