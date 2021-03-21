from datetime import datetime
from pathlib import Path
import discord
import requests
from discord.ext import commands

Discord_Bot_Dir = Path("./")
linksPath = Path(Discord_Bot_Dir / "resources/")
epicStoreFreeGamesAPI = "https://store-site-backend-static.ak.epicgames.com/freeGamesPromotions?locale=en-US&country=GB&allowCountries=GB,US"
epicGamesLogo = "https://upload.wikimedia.org/wikipedia/commons/thumb/3/31/Epic_Games_logo.svg/50px-Epic_Games_logo.svg.png"
epicStoreFreeGamesURL = "https://www.epicgames.com/store/en-US/free-games"


class EpicGames(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.cooldown(3, 30)
    @commands.command()
    async def epic(self, ctx):
        allGames = requests.get(epicStoreFreeGamesAPI).json()["data"]["Catalog"]["searchStore"]["elements"]
        
        currentGame = None
        for game in allGames:
            if game["promotions"]["promotionalOffers"]:
                currentGame = game
                break

        gameTimes = currentGame["promotions"]["promotionalOffers"][0]["promotionalOffers"][0]
        startTime = datetime.strptime(gameTimes["startDate"].split('T')[0], "%Y-%m-%d").strftime('%d %B %Y')
        endTime = datetime.strptime(gameTimes["endDate"].split('T')[0], "%Y-%m-%d").strftime('%d %B %Y')
        originalPrice = currentGame["price"]["totalPrice"]["fmtPrice"]["originalPrice"]
        gameCover = currentGame["keyImages"][1]["url"].replace(" ","%20")

        embed = discord.Embed(title=currentGame["title"],description=f"[Grab your free game here]({epicStoreFreeGamesURL})",colour=0x000000)
        embed.set_thumbnail(url=f"{epicGamesLogo}")
        embed.add_field(name="Start date", value=startTime, inline=False)
        embed.add_field(name="End date", value=endTime, inline=False)
        embed.add_field(name="Price", value="~~" + originalPrice + "~~ ⟶ Free", inline=False)
        embed.set_image(url=f"{gameCover}")

        await ctx.channel.send(embed=embed)

    @epic.error
    async def epic_error(self, ctx, error):
        await ctx.channel.send('error:  ' + str(error))


def setup(bot):
    bot.add_cog(EpicGames(bot))
