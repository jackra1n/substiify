from helper.ModulesManager import ModuleDisabledException, ModulesManager
from datetime import datetime, timedelta
from discord.ext import commands, tasks
from bs4 import BeautifulSoup
from utils import db
import logging
import discord
import requests

logger = logging.getLogger(__name__)

URL = "https://www.daydeal.ch/"
timeOffset = 2

class Daydeal(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.endTime = self.getDealEndTime()
        self.daydeal_task.start()

    def getSoup(self):
        page = requests.get(URL)
        return BeautifulSoup(page.content, 'html.parser')

    def getDealEndTime(self):
        soup = self.getSoup()
        return datetime.strptime(soup.find('div', class_='product-bar__offer-ends').findChild()['data-next-deal'], '%Y-%m-%d %H:%M:%S')  + timedelta(hours=timeOffset)

    async def availableBarCreator(self, available):
        toDraw = int(round(available, -1)/10)
        return '<:green_square:820409531573993513>'*toDraw + '<:grey_square:820409550938046514>'*(10-toDraw) + f' `{available}%`'

    async def createDaydealEmbed(self):
        # Web Scraping
        soup = self.getSoup()
        self.endTime = self.getDealEndTime()
        product_description = soup.find('section', class_='product-description')
        title1 = product_description.find('h1', class_='product-description__title1').text
        title2 = product_description.find('h2', class_='product-description__title2').text
        description_details = product_description.find('ul', class_='product-description__list').findChildren()
        product_img = soup.find('img', class_='product-img-main-pic')['src']
        new_price = soup.find('h2', class_='product-pricing__prices-new-price').text
        old_price = soup.find('span', class_='js-old-price')
        old_price = old_price.text if old_price is not None else ''
        available = int(soup.find('strong', class_='product-progress__availability').text.strip('%'))
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
        embed.set_footer(text=f'Ends in: {ends_in}')
        return embed

    @commands.cooldown(4, 10)
    @commands.group(invoke_without_command = True)
    @ModulesManager.register
    @commands.check(ModulesManager.is_enabled)
    async def daydeal(self, ctx):
        await ctx.channel.send(embed=await self.createDaydealEmbed())

    @daydeal.command()
    @commands.is_owner()
    async def daydealSetTimeOffset(self, ctx, offset: int):
        timeOffset = offset
    
    @daydeal.command()
    @commands.is_owner()
    async def getTimeOffset(self, ctx):
        await ctx.send(timeOffset)

    @daydeal.command()
    @commands.check(ModulesManager.is_enabled)
    @commands.has_permissions(manage_channels=True)
    async def setup(self, ctx, channel: discord.TextChannel = None, mention_role: discord.Role = None ):
        channel_id = ctx.channel.id if channel is None else channel.id
        mention_role_id = mention_role.id if mention_role is not None else None
        if db.session.query(db.Daydeal).filter_by(server_id=ctx.guild.id).first() is None:
            # Adds new db.Daydeal object to session
            db.session.add(db.Daydeal(ctx.guild.id, channel_id, mention_role_id))
            db.session.commit()     
            channel_to_send = ctx.guild.get_channel(channel_id)
            content = mention_role.mention if mention_role is not None else ''
            await channel_to_send.send(content=content, embed=await self.createDaydealEmbed())
            await ctx.channel.send(embed=discord.Embed(description='Setup successful', colour=0x23b40c))
        else:
            await ctx.channel.send(embed=discord.Embed(description='Daydeal is already set up', colour=0x23b40c), delete_after=10)

    @tasks.loop(seconds=60.0)
    async def daydeal_task(self):
        if datetime.now() >= self.endTime:
            daydealEmbed = await self.createDaydealEmbed()
            for setup in db.session.query(db.Daydeal).all():
                server = self.bot.get_guild(setup.server_id)
                channel = self.bot.get_channel(setup.channel_id)
                role = server.get_role(setup.role_id).mention if setup.role_id is not None else ''
                await channel.send(content=role,embed=daydealEmbed)

    @daydeal.command()
    @commands.check(ModulesManager.is_enabled)
    @commands.has_permissions(manage_channels=True)
    async def stop(self, ctx):
        db.session.query(db.Daydeal).filter_by(server_id=ctx.guild.id).delete()
        db.session.commit()
        await ctx.channel.send(embed=discord.Embed(description='Daydeal stopped', colour=0x23b40c))

    @daydeal.error
    async def daydeal_error(self, ctx, error):
        if not isinstance(error, ModuleDisabledException):
            await ctx.channel.send('Error:  ' + str(error))


def setup(bot):
    bot.add_cog(Daydeal(bot))
