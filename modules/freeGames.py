from datetime import datetime
import discord
import requests
from discord.ext import commands
import logging

logger = logging.getLogger(__name__)

epicStoreFreeGamesAPI = "https://store-site-backend-static.ak.epicgames.com/freeGamesPromotions"
epicGamesLogo = "https://upload.wikimedia.org/wikipedia/commons/thumb/3/31/Epic_Games_logo.svg/50px-Epic_Games_logo.svg.png"

class Game():
    def __init__(self, game_info_json: str) -> None:
        self.title = game_info_json["title"]
        self.start_date = datetime.strptime(game_info_json["effectiveDate"].split('T')[0], "%Y-%m-%d")
        self.end_date = self.getEndDate(game_info_json)
        self.original_price = game_info_json["price"]["totalPrice"]["fmtPrice"]["originalPrice"]
        self.discount_price = self.getGameDiscountPrice(game_info_json["price"])
        self.cover_image_url = self.getGameThumbnail(game_info_json["keyImages"])
        self.epic_store_link = f'https://www.epicgames.com/store/en-US/p/{game_info_json["productSlug"]}'

    def getEndDate(self, game_info_json: str) -> datetime:
        if game_info_json["promotions"] is not None:
            date_str = game_info_json["promotions"]["promotionalOffers"][0]["promotionalOffers"][0]["endDate"]
            return datetime.strptime(date_str.split('T')[0], "%Y-%m-%d")
        logger.info("Couldn't create free epic game. 'promotions' is 'None'")

    def getGameDiscountPrice(self, game_price_str: str) -> str:
        discount_price = game_price_str["totalPrice"]["fmtPrice"]["discountPrice"]
        if discount_price == "0":
            return "Free"
        return discount_price

    def getGameThumbnail(self, key_images: str) -> str:
        for image in key_images:
            if image["type"] == 'Thumbnail':
                return image["url"]

class FreeGames(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.cooldown(3, 30)
    @commands.command()
    async def epic(self, ctx):
        try:
            allGames = requests.get(epicStoreFreeGamesAPI).json()["data"]["Catalog"]["searchStore"]["elements"]
        except Exception as e:
            logger.error(f'Error while getting list of all Epic games: {e}')

        currentFreeGames = []
        for game in allGames:
            if datetime.strptime(game["effectiveDate"].split('T')[0], "%Y-%m-%d") <= datetime.now() and game["promotions"]:
                try:    
                    game = Game(game)
                    currentFreeGames.append(game)
                except Exception as e:
                    logger.error(f'Error while creating \'Game\' object: {e}')

        try:
            for game in currentFreeGames:
                startDateStr = game.start_date.strftime('%d %B %Y')
                endDateStr = game.end_date.strftime('%d %B %Y')
                embed = discord.Embed(title=game.title, url=game.epic_store_link, colour=0x000000)
                embed.set_thumbnail(url=f"{epicGamesLogo}")
                embed.add_field(name="Available", value=f'{startDateStr} to {endDateStr}', inline=False)
                embed.add_field(name="Price", value=f"~~`{game.original_price}`~~ ⟶ `{game.discount_price}`", inline=False)
                embed.set_image(url=f"{game.cover_image_url}")

                await ctx.channel.send(embed=embed)
        except Exception as e:
            logger.error(f'Fail while sending free game: {e}')

def setup(bot):
    bot.add_cog(FreeGames(bot))
