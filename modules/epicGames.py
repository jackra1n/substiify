from datetime import datetime
from pathlib import Path

import discord
import requests
from discord.ext import commands

Discord_Bot_Dir = Path("./")
linksPath = Path(Discord_Bot_Dir / "links/")
epicStoreFreeGamesURL = "https://store-site-backend-static.ak.epicgames.com/freeGamesPromotions?locale=en-US&country=GB&allowCountries=GB,US"


class EpicGames(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def epic(self, ctx):
        jsonEpicStore = requests.get(epicStoreFreeGamesURL).json()["data"]["Catalog"]["searchStore"]["elements"]
        currentGame = jsonEpicStore[0]
        gameTimes = currentGame["promotions"]["promotionalOffers"][0]["promotionalOffers"][0]
        startTime = datetime.strptime(gameTimes["startDate"].split('T')[0], "%Y-%m-%d").strftime('%d %B %Y')
        endTime = datetime.strptime(gameTimes["endDate"].split('T')[0], "%Y-%m-%d").strftime('%d %B %Y')

        embed = discord.Embed(title=currentGame["title"],description="[Grab your free game here](https://www.epicgames.com/store/en-US/free-games)",colour=0x000000)
        embed.set_thumbnail(url="https://upload.wikimedia.org/wikipedia/commons/thumb/3/31/Epic_Games_logo.svg/50px-Epic_Games_logo.svg.png")
        embed.add_field(name="Start date", value=startTime, inline=False)
        embed.add_field(name="End date", value=endTime, inline=False)
        embed.add_field(name="Price", value="~~" + currentGame["price"]["totalPrice"]["fmtPrice"]["originalPrice"] + "~~ ⟶ Free", inline=False)
        embed.set_image(url=currentGame["keyImages"][1]["url"])

        await ctx.channel.send(embed=embed)

    @epic.error
    async def epic_error(self, ctx, error):
        await ctx.channel.send('error:  ' + str(error))


def setup(bot):
    bot.add_cog(EpicGames(bot))
