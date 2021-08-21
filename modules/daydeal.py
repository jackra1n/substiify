from discord.ext.commands import BucketType
from datetime import datetime, timedelta
from discord.ext import commands, tasks
from bs4 import BeautifulSoup

from helper.ModulesManager import ModuleDisabledException, ModulesManager
from utils import db

import logging
import discord
import aiohttp

logger = logging.getLogger(__name__)

DAYDEAL_URL = 'https://www.daydeal.ch'
DAYDEAL_URL_WEEKLY = f'{DAYDEAL_URL}/deal-of-the-week'
timeOffset = 2

class Daydeal(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.end_time = ''
        self.end_time_weekly = ''
        self.prepare_task.start()
        if self.end_time and self.end_time_weekly:
            self.daydeal_task.start()

    @tasks.loop(seconds=60, count=1)
    async def prepare_task(self):
        self.end_time = await self.get_deal_end_time(DAYDEAL_URL)
        self.end_time_weekly = await self.get_deal_end_time(DAYDEAL_URL_WEEKLY)

    async def get_soup(self, url):
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                page = await resp.text()
                return BeautifulSoup(page, 'lxml')

    async def get_deal_end_time(self, url):
        soup = await self.get_soup(url)
        return datetime.strptime(soup.find('div', class_='product-bar__offer-ends').findChild()['data-next-deal'], '%Y-%m-%d %H:%M:%S')  + timedelta(hours=timeOffset)

    async def availableBarCreator(self, available):
        toDraw = int(round(available, -1)/10)
        return '<:green_square:820409531573993513>'*toDraw + '<:grey_square:820409550938046514>'*(10-toDraw) + f' `{available}%`'

    async def create_deal_embed(self, url):
        # Web Scraping
        soup = await self.get_soup(url)
        end_time = await self.get_deal_end_time(url)
        if url is DAYDEAL_URL:
            self.end_time = end_time
        if url is DAYDEAL_URL_WEEKLY:
            self.end_time_weekly = end_time
        product_description = soup.find('section', class_='product-description')
        title1 = product_description.find('h1', class_='product-description__title1').text
        title2 = product_description.find('h2', class_='product-description__title2').text
        description_details = product_description.find('ul', class_='product-description__list').findChildren()
        product_img = soup.find('img', class_='product-img-main-pic')['src']
        new_price = soup.find('h2', class_='product-pricing__prices-new-price').text
        old_price = soup.find('span', class_='js-old-price')
        old_price = old_price.text if old_price is not None else ''
        available = int(soup.find('strong', class_='product-progress__availability').text.strip('%'))
        ends_in = end_time - datetime.now().replace(microsecond=0)
        description_str = ""
        for element in description_details:
            description_str += "• " + element.text + "\n"

        # Create embed message
        embed = discord.Embed(title=title2, description=description_str, url=url, colour=0x23b40c)
        embed.set_thumbnail(url="https://static.daydeal.ch/2.17.10/images/logo-top.png")
        embed.set_image(url=product_img)
        title = 'Today\'s' if url == DAYDEAL_URL else 'This weeks'
        embed.set_author(name=f'{title} deal: ' + title1)
        embed.add_field(name="Price", value=f'~~`{old_price}`~~ ⟶ `{new_price}`', inline=False)
        embed.add_field(name="Available", value=str(await self.availableBarCreator(available)), inline=False)
        embed.set_footer(text=f'Ends in: {ends_in}')
        return embed

    @commands.cooldown(2, 900, BucketType.user)
    @commands.group(invoke_without_command = True)
    @ModulesManager.register
    @commands.check(ModulesManager.is_enabled)
    async def daydeal(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.channel.send(embed=await self.create_deal_embed(DAYDEAL_URL))

    @daydeal.command()
    async def weekly(self, ctx):
        await ctx.channel.send(embed=await self.create_deal_embed(DAYDEAL_URL_WEEKLY))

    @daydeal.command()
    @commands.is_owner()
    async def set_time_offset(self, ctx, offset: int):
        time_offset = offset
    
    @daydeal.command()
    @commands.is_owner()
    async def get_time_offset(self, ctx):
        await ctx.send(timeOffset)

    @daydeal.command()
    @commands.check(ModulesManager.is_enabled)
    @commands.has_permissions(manage_channels=True)
    async def setup(self, ctx, channel: discord.TextChannel = None, mention_role: discord.Role = None ):
        channel_id = ctx.channel.id if channel is None else channel.id
        mention_role_id = mention_role.id if mention_role is not None else None
        if db.session.query(db.daydeal).filter_by(server_id=ctx.guild.id).filter_by(channel_id=channel_id).first() is None:
            # Adds new db.Daydeal object to session
            db.session.add(db.daydeal(ctx.guild.id, channel_id, mention_role_id))
            db.session.commit()     
            channel_to_send = ctx.guild.get_channel(channel_id)
            content = mention_role.mention if mention_role is not None else ''
            await channel_to_send.send(content=content, embed=await self.create_deal_embed(DAYDEAL_URL_WEEKLY))
            await channel_to_send.send(content=content, embed=await self.create_deal_embed(DAYDEAL_URL))
            await ctx.channel.send(embed=discord.Embed(description=f'Setup successful in {channel_to_send.mention}', colour=0x23b40c))
        else:
            await ctx.channel.send(embed=discord.Embed(description='Daydeal is already set up', colour=0x23b40c), delete_after=10)

    @tasks.loop(seconds=60.0)
    async def daydeal_task(self):
        if datetime.now() >= self.end_time:
            await self.send_deal_embed(DAYDEAL_URL)
        if datetime.now() >= self.end_time_weekly:
            await self.send_deal_embed(DAYDEAL_URL_WEEKLY)
            
    async def send_deal_embed(self, url):
        daydeal_embed = await self.create_deal_embed(url)
        for setup in db.session.query(db.daydeal).all():
            server = self.bot.get_guild(setup.server_id)
            channel = self.bot.get_channel(setup.channel_id)
            role = server.get_role(setup.role_id).mention if setup.role_id is not None else ''
            await channel.send(content=role,embed=daydeal_embed)

    @daydeal.command()
    @commands.check(ModulesManager.is_enabled)
    @commands.has_permissions(manage_channels=True)
    async def stop(self, ctx, channel: discord.TextChannel = None):
        channel_id = ctx.channel.id if channel is None else channel.id
        channel = ctx.guild.get_channel(channel_id)
        db.session.query(db.daydeal).filter_by(server_id=ctx.guild.id).filter_by(channel_id=channel_id).delete()
        db.session.commit()
        await ctx.channel.send(embed=discord.Embed(description=f'Daydeal stopped in {channel.mention}', colour=0x23b40c))

    @daydeal.error
    async def daydeal_error(self, ctx, error):
        if not isinstance(error, ModuleDisabledException):
            await ctx.channel.send('Error:  ' + str(error))


def setup(bot):
    bot.add_cog(Daydeal(bot))
