from modules.PlayList import PlayList
from modules.YTDLSource import PlaylistHelper
from modules.YTDLSource import YTDLSource
from discord.ext import commands
import asyncio
import discord

class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.urls = None

    def check_queue(self, ctx):
        voice = discord.utils.get(self.bot.voice_clients, guild=ctx.guild)
        if voice is None:
            pass
        elif voice.is_connected() and not ctx.voice_client.is_playing():
            asyncio.run(self.play_next_song(ctx))
        else:
            pass

    def create_play_embed(self, title):
        return discord.Embed(
            title = f'Playing: {title}',
            description='Playing Song!',
            colour = discord.Colour.red()
        )

    def create_error_embed(self, err):
        return discord.Embed(
            title = f'ERROR: {err}',
            description='Playing Song!',
            colour = discord.Colour.dark_blue()
        )

    def create_queue_embed(self):
        return discord.Embed(
            title=f'Queued {len(self.urls)} Songs',
            description='Playing Song!',
            colour = discord.Colour.red()
        )

    @commands.command(aliases=["p"])
    async def play(self, ctx, *, url):
        if url.startswith('<'):
            url = url[1:-1]
        if PlaylistHelper.checkIfYoutubePlayList(url):
            self.urls = YTDLSource.get_playlist_info(url)['urls']
            await ctx.channel.send(embed=self.create_queue_embed())
            if not ctx.voice_client.is_playing():
                try:
                    player = await YTDLSource.from_url(self.urls.pop(0), stream=True)
                    if player is not None:
                        if ctx.voice_client.is_playing():
                            ctx.voice_client.stop()
                        ctx.voice_client.play(player, after=lambda e: self.check_queue(ctx))
                        await ctx.channel.send(embed=self.create_play_embed(player.title), delete_after=10)
                except Exception as err:
                    await ctx.channel.send(embed=self.create_error_embed(err))
            for entry in self.urls:
                PlayList.queue(entry)
        else:
            player = await YTDLSource.from_url(url, stream=True)
            if ctx.voice_client.is_playing():
                PlayList.queue(url)
            else:
                try:
                    if player is not None:
                        if ctx.voice_client.is_playing():
                            ctx.voice_client.stop()
                        ctx.voice_client.play(player, after=lambda e: self.check_queue(ctx))
                        await ctx.channel.send(embed=self.create_play_embed(player.title))
                except Exception as err:
                    await ctx.channel.send(embed=elf.create_error_embed(err))

    @commands.command()
    async def leave(self, ctx):
        self.urls = None
        server = ctx.message.guild.voice_client
        await server.disconnect()

    @commands.command()
    async def shuffle(self, ctx):
        PlayList.shuffle = not PlayList.shuffle
        title = f'Playlist unshuffled!'
        if PlayList.shuffle:
            title = f'Playlist shuffled!'
        await ctx.channel.send(embed=discord.Embed(title=title, colour=discord.Colour.dark_blue()))

    @commands.command()
    async def skip(self, ctx):
        await self.play_next_song(ctx)

    # @play.error
    # async def play_error(self, ctx, error):
    #     await ctx.channel.send('Cant play the song!')

    async def play_next_song(self, ctx):
        try:
            player = await PlayList.get_next_song()
            if player is not None:
                if ctx.voice_client.is_playing():
                    ctx.voice_client.stop()
                ctx.voice_client.play(player, after=lambda e: self.check_queue(ctx))
                await ctx.channel.send(embed=self.create_play_embed(player.title))
        except Exception as err:
            await ctx.channel.send(embed=self.create_error_embed(err))

    @play.before_invoke
    async def ensure_voice(self, ctx):
        if ctx.voice_client is None:
            if ctx.author.voice:
                await ctx.author.voice.channel.connect()
            else:
                await ctx.channel.send("You are not connected to a voice channel.")
                raise commands.CommandError("Author not connected to a voice channel.")

    @commands.command()
    async def summon(self, ctx):
        await ctx.author.voice.channel.connect()

def setup(bot):
    bot.add_cog(Music(bot))