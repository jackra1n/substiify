import discord
from discord.ext import commands
from YTDLSource import YTDLSource
from YTDLSource import PlaylistHelper
from PlayList import PlayList

class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def check_queue(self, ctx):
        if not ctx.voice_client.is_playing():
            asyncio.run(play_next_song(ctx))
        else:
            pass

    @commands.command(pass_context=True, aliases=["p", "sing"])
    async def play(self, ctx, *, url):
        if PlaylistHelper.checkIfYoutubePlayList(url):
            urls = YTDLSource.get_playlist_info(url)['urls']
            embed = discord.Embed(
                title="Queued " + str(len(urls)) + " Songs",
                description='Playing Song!',
                colour = discord.Colour.red()
            )
            await ctx.channel.send(embed=embed)

            if not ctx.voice_client.is_playing():
                try:
                    player = await YTDLSource.from_url(urls.pop(0), stream=True)
                    if player is not None:
                        if ctx.voice_client.is_playing():
                            ctx.voice_client.stop()
                        ctx.voice_client.play(player, after=lambda e: check_queue(ctx))
                        embed = discord.Embed(
                            title = 'Playing: ' + player.title,
                            description='Playing Song!',
                            colour = discord.Colour.red()
                        )
                        await ctx.channel.send(embed=embed)
                except Exception as err:
                    embed = discord.Embed(
                        title = 'ERROR: {0}'.format(err),
                        description='Playing Song!',
                        colour = discord.Colour.dark_blue()
                    )
                    await ctx.channel.send(embed=embed)

            for entry in urls:
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
                        ctx.voice_client.play(player, after=lambda e: check_queue(ctx))
                        embed = discord.Embed(
                            title = 'Playing: ' + player.title,
                            description='Playing Song!',
                            colour = discord.Colour.red()
                        )
                        await ctx.channel.send(embed=embed)
                except Exception as err:
                    embed = discord.Embed(
                        title = 'ERROR: {0}'.format(err),
                        description='Playing Song!',
                        colour = discord.Colour.dark_blue()
                    )
                    await ctx.channel.send(embed=embed)

    @commands.command(pass_context=True, aliases=["l", "disconnect"])
    async def leave(self, ctx):
        server = ctx.message.guild.voice_client
        await server.disconnect()

    @commands.command(pass_context=True, aliases=["r", "random"])
    async def shuffle(self, ctx):
        PlayList.shuffle = not PlayList.shuffle

    @commands.command()
    async def skip(self, ctx):
        await play_next_song(ctx)

    @play.error
    async def play_error(self, ctx, error):
        await ctx.channel.send('Cant play the song!')

    async def play_next_song(self, ctx):
        try:
            player = await PlayList.get_next_song()
            if player is not None:
                if ctx.voice_client.is_playing():
                    ctx.voice_client.stop()
                ctx.voice_client.play(player, after=lambda e: check_queue(ctx))
                embed = discord.Embed(
                    title = 'Playing: ' + player.title,
                    description='Playing Song!',
                    colour = discord.Colour.red()
                )
                await ctx.channel.send(embed=embed)
        except Exception as err:
            embed = discord.Embed(
                title = 'ERROR: {0}'.format(err),
                description='Playing Song!',
                colour = discord.Colour.dark_blue()
            )
            await ctx.send(embed=embed)

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