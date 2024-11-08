from pytubefix import YouTube, Stream
from instaloader import Post, Instaloader
import random, os, re, sys, requests, subprocess
from bs4 import BeautifulSoup
from tqdm import tqdm
from logs import log

class WebDownloader:
    def __init__(self, url):
        self.url = url
        self.output_path = os.path.join(os.path.dirname(__file__), 'output')
        self.check_url_website()    

    def check_url_website(self):
        log(self.url, "DEBUG")
        if 'youtube.com' in self.url:
            youtube = YoutubeDownloader(self.url, self.output_path)
            youtube.download_youtube_video()
        elif 'twitter.com' in self.url or 'x.com' in self.url:
            twitter = TwitterDownloader(self.url, self.output_path)
            twitter.download_twitter_video()
        elif 'instagram.com' in self.url:
            instagram = InstagramDownloader(self.url, self.output_path)
            instagram.download_instagram_post()
        elif 'spotify.com' in self.url:
            return 'spotify'
        else:
            return None

    def download_spotify_audio(url, output_path):
        # Download the audio using requests or another method
        # spotdl https://open.spotify.com/track/your_track_id
        pass

class YoutubeDownloader():
    def __init__(self, url, output_path, quality='highest', media='video', extension='mp4'):
        super().__init__()
        self.url = url
        self.output_path = output_path
        self.quality = quality
        self.media = media
        self.extension = extension

    def download_youtube_video(self):
        yt = YouTube(self.url)
        stream = self.set_stream(yt)
        final_file_name = self.set_name(stream)
        
        log(f"Downloading {final_file_name} in {self.media} media with {self.quality} quality", "INFO")
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
        
        if self.media == 'video':
            if self.quality == 'highest':
                stream = yt.streams.get_highest_resolution()
            else:
                stream = yt.streams.filter(res=self.quality, file_extension=self.extension).first()
        elif self.media == 'audio':
            stream = yt.streams.filter(only_audio=True).first()

        return stream
    
    def set_name(self, stream: Stream):
        file_extension = stream.mime_type.split('/')[1]
        file_name = stream.default_filename.replace("|", "_")
        base_name, ext = os.path.splitext(file_name)
        
        base_name = base_name.replace("|", "_").replace(":", "_").replace("*", "_").replace("?", "_").replace("\"", "_").replace("<", "_").replace(">", "_").replace("\\", "_").replace("/", "_")
        
        final_file_name = f"{base_name}{ext}"
        while os.path.exists(os.path.join(self.output_path, final_file_name)):
            log(os.path.join(self.output_path, final_file_name), "DEBUG")
            random_number = random.randint(1000, 9999)
            final_file_name = f"{base_name}_{random_number}{ext}"
        
        return final_file_name
    
class InstagramDownloader:
    def __init__(self, url, output_path, format='mp4'):
        self.url = url
        self.output_path = output_path
        self.format = format
        self.loader = Instaloader()

    def download_instagram_post(self):
        post = Post.from_shortcode(self.loader.context, self.url.split('/')[-2])
        if post.is_video:
            self.download_video(post)
        else:
            self.download_image(post)

    def download_video(self, post):
        if self.format not in ['mp4', 'webm']:
            log(f"Format {self.format} not supported for videos. Defaulting to mp4.", "WARNING")
            self.format = 'mp4'
        video_url = post.video_url
        self.download_file(video_url, post, self.format)

    def download_image(self, post):
        if self.format not in ['jpg', 'png']:
            log(f"Format {self.format} not supported for images. Defaulting to jpg.", "WARNING")
            self.format = 'jpg'
        image_url = post.url
        self.download_file(image_url, post, self.format)

    def download_file(self, file_url, post, extension):
        base_name = post.shortcode
        log(f"Base name: {base_name}", "DEBUG")
        final_file_name = self.get_unique_output_file(base_name, extension)
        log(f"Downloading {final_file_name} from {file_url}", "INFO")
        self.loader.download_pic(final_file_name.rsplit(".", 1)[0], file_url, post.date_utc)

    def get_unique_output_file(self, base_name, extension):
        output_file = os.path.join(self.output_path, f'{base_name}_converted.{extension}')
        while os.path.exists(output_file):
            random_number = random.randint(1, 10000)
            output_file = os.path.join(self.output_path, f'{base_name}_converted_{random_number}.{extension}')
        return output_file

class TwitterDownloader:
    def __init__(self, url, output_path, format="mp4"):
        self.url = url
        self.output_path = output_path
        self.format = format

    def get_unique_output_file(self, base_name, extension):
        output_file = os.path.join(self.output_path, f'{base_name}.{extension}')
        while os.path.exists(output_file):
            random_number = random.randint(1, 10000)
            output_file = os.path.join(self.output_path, f'{base_name}_{random_number}.{extension}')
        return output_file

    def download_video(self, url, file_name) -> None:
        """Download a video from a URL into a filename.

        Args:
            url (str): The video URL to download
            file_name (str): The file name or path to save the video to.
        """
        response = requests.get(url, stream=True)
        total_size = int(response.headers.get("content-length", 0))
        block_size = 1024
        progress_bar = tqdm(total=total_size, unit="B", unit_scale=True, colour="red")

        download_path = os.path.join(self.output_path, file_name)

        with open(download_path, "wb") as file:
            for data in response.iter_content(block_size):
                progress_bar.update(len(data))
                file.write(data)

        progress_bar.close()
        log(f"Downloaded {file_name} from {url}", "INFO")

    def download_twitter_video(self):
        """Extract the highest quality video url to download into a file

        Args:
            url (str): The twitter post URL to download from
        """

        api_url = f"https://twitsave.com/info?url={self.url}"

        response = requests.get(api_url)
        data = BeautifulSoup(response.text, "html.parser")
        download_button = data.find_all("div", class_="origin-top-right")[0]
        quality_buttons = download_button.find_all("a")
        highest_quality_url = quality_buttons[0].get("href")  # Highest quality video url

        file_name = data.find_all("div", class_="leading-tight")[0].find_all("p", class_="m-2")[0].text  # Video file name
        file_name = re.sub(r"[^a-zA-Z0-9]+", ' ', file_name).strip() + f".{self.format}"  # Remove special characters from file name

        unique_file_name = self.get_unique_output_file(file_name.rsplit('.', 1)[0], self.format)
        self.download_video(highest_quality_url, unique_file_name)

    def check_url_website(self):
        if len(sys.argv) < 2:
            log("Please provide the Twitter video URL as a command line argument.\nEg: python twitter_downloader.py <URL>", "ERROR")
        else:
            self.url = sys.argv[1]
            if self.url:
                self.download_twitter_video(self.url)
            else:
                log("Invalid Twitter video URL provided.", "ERROR")

class SpotifyDownloader:
    def __init__(self, url, output_path):
        self.url = url
        self.output_path = output_path
        
    def check_spotify_type(self):
        if 'track' in self.url:
            self.type = 'track'
        elif 'album' in self.url:
            self.type = 'album'
        elif 'playlist' in self.url:
            self.type = 'playlist'
        else:
            raise ValueError("Unsupported Spotify URL type")

    def download_spotify_audio(self):
        self.check_spotify_type()
        command = [
            'spotdl',
            'download',
            self.url,
            '--output', self.output_path
        ]
        try:
            subprocess.run(command, check=True)
            print(f"Downloaded successfully to {self.output_path}")
        except subprocess.CalledProcessError as e:
            print(f"Error during download: {e}")

# Example usage
if __name__ == "__main__":
    url = "https://open.spotify.com/intl-fr/track/180f6yuE1mPjD2hs5fdxLm?si=47670c310d944aef"  # Replace with your Spotify URL
    url = "https://open.spotify.com/playlist/37i9dQZF1EpiylCZQ6XZD4?si=f40e99cc1b014363" # Playlist
    url = "https://open.spotify.com/intl-fr/album/0DsMhU0ERzMt6xvtGpgXvW?si=8UmBjpT6Qbe0STQvgKyRlg" # Album
    output_path = "C:/Users/Siphano/Documents/VSCODE/Ultimate-Converter/src/output"  # Replace with your desired output path
    downloader = SpotifyDownloader(url, output_path)
    downloader.download_spotify_audio()

# if __name__ == "__main__":
#     # downloader = WebDownloader("https://www.youtube.com/watch?v=icPHcK_cCF4&pp=ygUXeW91dHViZSA1IHNlY29uZHMgdmlkZW8%3D")
#     # downloader = WebDownloader("https://www.instagram.com/zurgloxleterrible/p/C61bFusC8ce/?hl=hu  ")
#     downloader = WebDownloader("https://x.com/JixonKds/status/1854489456423666137")