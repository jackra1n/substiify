from discord import PCMVolumeTransformer, FFmpegPCMAudio
from functools import partial
import youtube_dl
import logging
import asyncio

ytdl_format_options = {
    'format': 'bestaudio/best',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0',  # bind to ipv4 since ipv6 addresses cause issues sometimes
    'noplaylist': False,
    'flat-playlist': True
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)

ffmpeg_options = {
    'options': '-vn'
}

class YTDLSource(PCMVolumeTransformer):
    def __init__(self, source, *, data, requester, volume=0.5):
        super().__init__(source, volume)

        self.data = data
        self.title = data.get('title')
        self.url = data.get('url')
        self.requester = requester


    def __getitem__(self, item: str):
        """Allows us to access attributes similar to a dict.
        This is only useful when you are NOT downloading.
        """
        return self.__getattribute__(item)

    @classmethod
    async def from_url(cls, ctx, url, *, loop, stream=False):
        try:
            loop = loop or asyncio.get_event_loop()
            to_run = partial(ytdl.extract_info, url=url, download=not stream)
            data = await loop.run_in_executor(None, to_run)
            if 'entries' in data:
                # take first item from a playlist
                data = data['entries'][0]

            filename = data['url'] if stream else ytdl.prepare_filename(data)
            return cls(FFmpegPCMAudio(filename, **ffmpeg_options), data=data, requester=ctx.author)
        except Exception as e:
            logging.critical(f'***Exception while getting video info***:\n {e}\n')

    @classmethod
    async def regather_stream(cls, data, *, loop):
        loop = loop or asyncio.get_event_loop()

        to_run = partial(ytdl.extract_info, url=data['webpage_url'], download=False)
        data = await loop.run_in_executor(None, to_run)
        return cls(discord.FFmpegPCMAudio(data['url']), data=data)

    @classmethod
    def get_playlist_info(self, url: str):
        # in case of a radio playist, restrict the number of songs that are downloaded
        # if we received just the id, it is an id starting with 'RD'
        # if its a url, the id is behind a '&list='
        #if song_utils.is_radio(self.target):
        #    self.ydl_opts['playlistend'] = self.musiq.base.settings.max_playlist_items

        with youtube_dl.YoutubeDL(ytdl_format_options) as ydl:
            self.info_dict = ydl.extract_info(url=url, download=False, process=False)

        if self.info_dict['_type'] != 'playlist' or 'entries' not in self.info_dict:
            raise Exception('Not a Playlist')

        playlist_info = {}
        playlist_info['id'] = self.info_dict['id']
        playlist_info['urls'] = []
        if 'title' in self.info_dict:
            playlist_info['title'] = self.info_dict['title']
        for entry in self.info_dict['entries']:
            playlist_info['urls'].append('https://www.youtube.com/watch?v=' + entry['id'])
        return playlist_info