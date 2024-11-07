from pytubefix import YouTube, Stream
import instaloader
import snscrape.modules.twitter as sntwitter
from logs import log
import random, os

class WebDownloader:
    def __init__(self, url):
        self.url = url
        self.output_path = os.path.join(os.path.dirname(__file__), 'output')
        self.check_url_website()    

    def check_url_website(self):
        if 'youtube.com' in self.url:
            youtube = YoutubeDownloader(self.url, self.output_path)
            youtube.download_youtube_video()
        elif 'twitter.com' in self.url:
            return 'twitter'
        elif 'instagram.com' in self.url:
            return 'instagram'
        elif 'spotify.com' in self.url:
            return 'spotify'
        else:
            return None

    def download_twitter_video(tweet_url):
        tweet_id = tweet_url.split('/')[-1]
        tweet = sntwitter.TwitterTweetScraper(tweet_id).get_item()
        for media in tweet.media:
            if media.type == 'video':
                video_url = media.variants[0].url
                # Download the video using requests or another method

    def download_instagram_post(url, output_path):
        loader = instaloader.Instaloader()
        post = instaloader.Post.from_shortcode(loader.context, url.split('/')[-2])
        loader.download_post(post, target=output_path)


    def download_spotify_audio(url, output_path):
        # Download the audio using requests or another method
        # spotdl https://open.spotify.com/track/your_track_id
        pass

class YoutubeDownloader():
    def __init__(self, url, output_path, quality='highest', format='video', extension='mp4'):
        super().__init__()
        self.url = url
        self.output_path = output_path
        self.quality = quality
        self.format = format
        self.extension = extension

    def download_youtube_video(self):
        yt = YouTube(self.url)
        stream = self.set_stream(yt)
        final_file_name = self.set_name(stream)
        
        log(f"Downloading {final_file_name} in {self.format} format with {self.quality} quality", "INFO")
        stream.download(self.output_path, filename=final_file_name)

    def get_resolutions(self, yt: YouTube):
        resolutions = []
        for stream in yt.streams:
            if stream.resolution and stream.resolution not in resolutions:
                resolutions.append(stream.resolution)
        resolutions.sort(key=lambda x: int(x.replace('p', '')))

        return resolutions
    
    def set_stream(self, yt: YouTube):
        resolutions = self.get_resolutions(yt)
        
        if self.format == 'video':
            if self.quality == 'highest':
                stream = yt.streams.get_highest_resolution()
            else:
                stream = yt.streams.filter(res=self.quality, file_extension=self.extension).first()
        elif self.format == 'audio':
            stream = yt.streams.filter(only_audio=True).first()

        return stream
    
    def set_name(self, stream: Stream):
        file_extension = stream.mime_type.split('/')[1]
        file_name = stream.default_filename.replace("|", "_")
        base_name, ext = os.path.splitext(file_name)
        
        base_name = base_name.replace("|", "_").replace(":", "_").replace("*", "_").replace("?", "_").replace("\"", "_").replace("<", "_").replace(">", "_").replace("\\", "_").replace("/", "_")
        
        final_file_name = f"{base_name}{ext}"
        while os.path.exists(os.path.join(self.output_path, final_file_name)):
            print(os.path.join(self.output_path, final_file_name))
            random_number = random.randint(1000, 9999)
            final_file_name = f"{base_name}_{random_number}{ext}"
        
        return final_file_name

if __name__ == "__main__":
    downloader = WebDownloader("https://www.youtube.com/watch?v=icPHcK_cCF4&pp=ygUXeW91dHViZSA1IHNlY29uZHMgdmlkZW8%3D")