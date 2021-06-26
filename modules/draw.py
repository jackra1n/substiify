from websocket import create_connection
from discord.ext import commands
from discord import File
from PIL import Image
import requests
import logging
import asyncio
import os

logger = logging.getLogger(__name__)

class Drawing(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.place_canvas = None
        self.drawing_queue = []

    @commands.command()
    @commands.is_owner()
    async def secretDraw(self, ctx, offsetX:int=0, offsetY:int=0, resizeX:int=None, resizeY:int=None):
        imageToDraw = await self.getImage(ctx, resizeX, resizeY)
        width, height = imageToDraw.size
        pix = list(imageToDraw.getdata())

        fileTxt = open('pixelart.txt','w')
        await ctx.invoke(self.get_canvas_ws)
        place_canvas = self.place_canvas.convert('L')
        place_canvas = place_canvas.convert('RGB')

        pixel_count = 0
        while pixel_count <= 3600:
            for x in range(width):
                for y in range(height):
                    canvas_clr = self.place_canvas.getpixel((x+offsetX,y+offsetY))
                    clr = pix[x+y*width]
                    if clr[:-1] != canvas_clr and clr != (0,0,0,0):
                        pixel_count += 1
                        place_canvas.putpixel((x+offsetX, y+offsetY), clr[:-1])
                        fileTxt.write(f"{x+offsetX} {y+offsetY} {self.rgbToHex(clr[:-1])}|")

        place_canvas.save("place.png")
        if os.stat('place.png').st_size <= 8000000:
            await ctx.send(file=File(Image.open('place.png').filename))
        else:
            await ctx.send(f'file "palce.png" too big')
        if os.stat(fileTxt.name).st_size <= 8000000:
            await ctx.send(file=File(fileTxt.name))
        else:
            await ctx.send(f'file "{fileTxt.name}" too big')
        fileTxt.close()

    @commands.command()
    @commands.is_owner()
    async def spamDraw2(self, ctx, offsetX:int=0, offsetY:int=0, resizeX:int=None, resizeY:int=None):
        await self.draw_loop(ctx, ctx.channel, offsetX, offsetY, resizeY, resizeY)

    @commands.command()
    @commands.is_owner()
    async def spamDraw(self, ctx, offsetX:int=0, offsetY:int=0, resizeX:int=None, resizeY:int=None):
        server = self.bot.get_guild(747752542741725244)
        channelToSpam = server.get_channel(819966095070330950)
        await self.draw_loop(ctx, channelToSpam, offsetX, offsetY, resizeY, resizeY)
        await ctx.send('Drawing done!')

    async def getImage(self, ctx, resX, resY):
        try:
            image = Image.open(requests.get(ctx.message.attachments[0].url, stream=True).raw).convert('RGBA')
        except Exception as e:
            await ctx.send(f'Could not get or convert the image to RGBA: {e}')
        if image is not None and resX and resY:
            image = image.resize((resX,resY))
        return image

    def rgbToHex(self, rgbTuple):
        return '#%02x%02x%02x' % rgbTuple
            
    async def draw_loop(self, ctx, channel, offX, offY, resX, resY):
        await ctx.invoke(self.get_canvas_ws)
        image = await self.getImage(ctx, resX, resY)
        width, height = image.size
        pix = list(image.getdata())
        for x in range(width):
            for y in range(height):
                clr = pix[x+y*width]
                canvas_clr = self.place_canvas.getpixel((x+offX,y+offY))
                if clr[:-1] != canvas_clr and clr[-1] > 230:
                    await channel.send(f".place setpixel {x+offX} {y+offY} {self.rgbToHex(clr[:-1])}")

    @commands.command()
    @commands.is_owner()
    async def get_canvas_ws(self, ctx):
        try:
            ws = create_connection("ws://137.135.102.90:9000/place")
            ws.send('\x01')
            ba = bytearray(ws.recv())
            ws.close()
            del ba[0] # BattleRush said to delete 1st element

            width, height = 1000, 1000
            self.place_canvas = Image.new('RGB', (width,height))

            index = 0
            for i in range(width):
                for j in range (height):
                    color = (ba[index], ba[index+1], ba[index+2])
                    index += 3
                    self.place_canvas.putpixel((j,i), color)
            self.place_canvas.save('place.png')
            await ctx.send('Got the newest canvas', delete_after=60)
        except Exception as e:
            await ctx.send(f'Problem while getting canvas: {e}\nTrying again...', delete_after=3)
            await ctx.invoke(self.get_canvas_ws)

    @commands.command()
    @commands.is_owner()
    async def get_canvas(self, ctx):
        server = self.bot.get_guild(747752542741725244)
        channel = server.get_channel(768600365602963496)
        rushs_helper = server.get_member(774276700557148170)
        await channel.send('.place view', delete_after=1)
        await asyncio.sleep(3)
        for message in rushs_helper.history(limit=30):
            if message.attachments[0].filename == 'place.png':
                self.place_canvas = Image.open(requests.get(message.attachments[0].url, stream=True).raw)
        await ctx.send('Got the newest canvas', delete_after=20)

def setup(bot):
    bot.add_cog(Drawing(bot))
