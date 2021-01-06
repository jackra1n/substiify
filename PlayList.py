from YTDLSource import YTDLSource
import random

class PlayList:
    shuffle = False
    youtube_sources = []

    @classmethod
    def queue(cls, youtubeSource:str):
        cls.youtube_sources.append(youtubeSource)
        print("queued: " + youtubeSource)

    @classmethod
    async def get_next_song(cls):
        if len(cls.youtube_sources) == 0:
            return ""
        else:
            if cls.shuffle:
                new_song = random.randint(0, len(cls.youtube_sources) - 1)
                youtube_source = cls.youtube_sources[new_song]
                cls.youtube_sources.pop(new_song)
            else:
                youtube_source = cls.youtube_sources[0]
                cls.youtube_sources.pop(0)
            return await YTDLSource.from_url(youtube_source, stream=True)
