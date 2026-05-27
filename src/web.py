import os
from logs import log
from youtube_downloader import YoutubeDownloader
from instagram_downloader import InstagramDownloader
from twitter_downloader import TwitterDownloader
from reddit_downloader import RedditDownloader
from spotify_downloader import SpotifyDownloader

class WebDownloader:
    def __init__(self, url, format, resolution='best', codec='best'):
        self.url = url
        self.format = format
        self.resolution = resolution
        self.codec = codec
        
        self.filename: str
        self.medias_list: list[str] = []
        self.output_path = os.path.join(os.path.dirname(__file__), 'output')

    def setup_download(self):
        log(self.url, "DEBUG")
        url_lower = self.url.lower()
        log(url_lower, "DEBUG")
        try:
            if 'youtube' in url_lower or 'youtu.be' in url_lower or 'tiktok' in url_lower:
                web_dl = YoutubeDownloader(self.url, self.output_path, format=self.format, resolution=self.resolution, codec=self.codec)
                web_dl.download()
            elif 'reddit' in url_lower or 'redd.it' in url_lower:
                web_dl = RedditDownloader(self.url, self.output_path, format=self.format)
                web_dl.download()
            elif 'twitter' in url_lower or 'x.com' in url_lower:
                web_dl = TwitterDownloader(self.url, self.output_path, format=self.format)
                web_dl.download()
            elif 'instagram' in url_lower:
                web_dl = InstagramDownloader(self.url, self.output_path, format=self.format)
                web_dl.download()
            elif 'spotify' in url_lower:
                web_dl = SpotifyDownloader(self.url, self.output_path, format=self.format)
                web_dl.download()
            else:
                return None
            self.filename = web_dl.final_file_name
            self.medias_list = web_dl.medias_list
            return True
        except Exception as e:
            log(f"Server error during download: {e}", level="CRITICAL")
            return None
