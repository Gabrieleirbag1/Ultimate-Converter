from pytubefix import YouTube, Stream, Playlist
from instaloader import Post, Instaloader
import random, os, re, sys, requests, subprocess, string, zipfile, uuid
from bs4 import BeautifulSoup
from tqdm import tqdm
from logs import log
from converter import ClassicConverter

class FileManager:
    def __init__(self, media_files: list[str], output_path: str, media_title: str):
        self.media_files = media_files
        self.output_path = output_path
        self.media_title = media_title

        self.zip_final_filename: str

    def get_unique_output_file(self):
        zip_final_filename = os.path.join(self.output_path, f"{self.media_title}.zip")
        while os.path.exists(zip_final_filename):
            random_number = random.randint(1, 10000)
            zip_final_filename = os.path.join(self.output_path, f"{self.media_title}_{random_number}.zip")
        self.zip_final_filename = zip_final_filename

    def remove_uploaded_file(self, file_path: str):
        try:
            os.remove(file_path)
        except FileNotFoundError:
            pass

    def make_archive(self):
        self.get_unique_output_file()
        with zipfile.ZipFile(self.zip_final_filename, 'w') as zipf:
            for file in self.media_files:
                log(f"Adding {file} to archive", "DEBUG")
                file_path = os.path.join(self.output_path, file)
                try:
                    zipf.write(file_path, arcname=os.path.basename(file_path))
                except FileNotFoundError:
                    continue
                self.remove_uploaded_file(file_path)

class YoutubeDownloader():
    def __init__(self, url, output_path, quality='highest', media='video', format='mp4'):
        super().__init__()
        self.url = url
        self.output_path = output_path
        self.quality = quality
        self.media = media
        self.format = format

        self.final_file_name: str
        self.medias_list: list[str] = []

    def download(self):
        if 'playlist' in self.url:
            self.download_playlist()
        else:
            self.download_video()

    def convert_file(self, extension):
        file_path = os.path.join(self.output_path, self.final_file_name)
        if self.format != extension:
            converter = ClassicConverter(file_path, self.format)
            if not converter.convert():
                log(f"Error converting file: {self.final_file_name}", "ERROR")
            if os.path.exists(self.final_file_name):
                os.remove(self.final_file_name)
            self.final_file_name = converter.output_file

    def download_video(self):
        yt = YouTube(self.url)
        stream = self.set_stream(yt)
        self.final_file_name = self.set_name(stream)
        
        log(f"Downloading {self.final_file_name} in {self.media} media with {self.quality} quality", "INFO")
        stream.download(self.output_path, filename=self.final_file_name)
        self.convert_file(stream.mime_type.split('/')[1])

    def download_playlist(self):
        playlist = Playlist(self.url)
        try:
            log(f"Downloading playlist: {playlist.title}", "INFO")
            for video in playlist.videos:
                self.url = video.watch_url
                self.download_video()
                self.medias_list.append(self.final_file_name)
            playlist_title = re.sub(r'[|:*?"<>\\/]', '_', playlist.title)
            file_manager = FileManager(self.medias_list, self.output_path, playlist_title)
            file_manager.make_archive()
            self.final_file_name = file_manager.zip_final_filename
        except KeyError as e:
            log(f"Error downloading playlist: {e}", "ERROR")

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
                stream = yt.streams.filter(res=self.quality, file_extension=self.format).first()
        elif self.media == 'audio':
            stream = yt.streams.filter(only_audio=True).first()

        return stream
    
    def set_name(self, stream: Stream):
        file_extension = stream.mime_type.split('/')[1]
        file_name = stream.default_filename.replace("|", "_")
        base_name, ext = os.path.splitext(file_name)
        base_name = re.sub(r'[|:*?"<>\\/]', '_', file_name.rsplit('.', 1)[0])
        if str.isspace(base_name) or not base_name:
            base_name = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
        if len(base_name) > 50:
            base_name = base_name[:50]
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

        self.final_file_name: str
        self.medias_list: list[str] = []

    def download(self):
        post = Post.from_shortcode(self.loader.context, self.url.split('/')[-2])
        if post.is_video:
            self.download_video(post)
        else:
            self.download_image(post)
        
    def convert_file(self, extension):
        if self.format != extension:
            converter = ClassicConverter(self.final_file_name, self.format)
            if not converter.convert():
                log(f"Error converting file: {self.final_file_name}", "ERROR")
            if os.path.exists(self.final_file_name):
                os.remove(self.final_file_name)
            self.final_file_name = converter.output_file

    def download_video(self, post):
        if self.format not in ['mp4', 'webm']:
            log(f"Format {self.format} not supported for videos. Defaulting to mp4.", "WARNING")
            extension = 'mp4'
        else:
            extension = self.format
        video_url = post.video_url
        self.download_file(video_url, post, extension)

    def download_image(self, post):
        if self.format not in ['jpg', 'png']:
            log(f"Format {self.format} not supported for images. Defaulting to jpg.", "WARNING")
            extension = 'jpg'
        else:
            extension = self.format
        image_url = post.url
        self.download_file(image_url, post, extension)

    def generate_file_name(self, file_name, extension):
        base_name = re.sub(r'[|:*?"<>\\/]', '_', file_name.rsplit('.', 1)[0])
        log(f"Base name: {base_name}", "DEBUG")
        if str.isspace(base_name) or not base_name:
            base_name = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
        if len(base_name) > 50:
            base_name = base_name[:50]
        self.final_file_name = self.get_unique_output_file(base_name, extension)

    def download_file(self, file_url, post, extension):
        file_name = post.shortcode
        self.generate_file_name(file_name, extension)
        log(f"Downloading {self.final_file_name} from {file_url}", "INFO")
        self.loader.download_pic(self.final_file_name.rsplit(".", 1)[0], file_url, post.date_utc)
        self.convert_file(extension)

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

        self.final_file_name: str
        self.medias_list: list[str] = []

    def download(self):
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

        self.generate_file_name(data)
        self.download_video(highest_quality_url, self.final_file_name)
            
    def convert_file(self, extension):
        if self.format != extension:
            converter = ClassicConverter(self.final_file_name, self.format)
            if not converter.convert():
                log(f"Error converting file: {self.final_file_name}", "ERROR")
            if os.path.exists(self.final_file_name):
                os.remove(self.final_file_name)
            self.final_file_name = converter.output_file

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
        self.convert_file("mp4")

    def generate_file_name(self, data):
        file_name = data.find_all("div", class_="leading-tight")[0].find_all("p", class_="m-2")[0].text  # Video file name
        file_name = re.sub(r"[^a-zA-Z0-9]+", ' ', file_name).strip() + f".{self.format}"  # Remove special characters from file name
        base_name = re.sub(r'[|:*?"<>\\/]', '_', file_name.rsplit('.', 1)[0])
        if str.isspace(base_name) or not base_name:
            base_name = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
        if len(base_name) > 50:
            base_name = base_name[:50]
        log(f"Base name: {base_name}", "DEBUG")
        self.final_file_name = self.get_unique_output_file(base_name, "mp4")

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
    def __init__(self, url, output_path, format):
        self.url = url
        self.output_path = output_path
        self.format = format

        self.final_file_name: str = ""
        self.medias_list: list[str] = []
        self.media_title: str = ""
        self.unique_dir: str = ""

    def check_spotify_type(self):
        if 'track' in self.url:
            self.type = 'track'
        elif 'album' in self.url:
            self.type = 'album'
        elif 'playlist' in self.url:
            self.type = 'playlist'
        else:
            raise ValueError("Unsupported Spotify URL type")

    def create_unique_directory(self):
        unique_id = str(uuid.uuid4())
        self.unique_dir = os.path.join(self.output_path, unique_id)
        os.makedirs(self.unique_dir, exist_ok=True)

    def remove_unique_directory(self):
        try:
            os.rmdir(self.unique_dir)
        except OSError:
            pass

    def download(self):
        self.check_spotify_type()
        self.create_unique_directory()
        command = [
            'spotdl',
            'download',
            self.url,
            '--output', self.unique_dir,
        ]
        try:
            result = subprocess.run(command, check=True, capture_output=True, text=True)
            log(f"Downloaded successfully to {self.unique_dir}", "INFO")
            output = result.stdout
            log(output, "DEBUG")
            if self.type == 'track':
                self.set_final_file_name_for_track()
            else:
                self.set_medias_list_for_album_or_playlist(output)
                self.create_zip_for_album_or_playlist()
                self.remove_unique_directory()
        except subprocess.CalledProcessError as e:
            log(f"Error during download: {e}", "ERROR")

    def set_final_file_name_for_track(self):
        files = os.listdir(self.unique_dir)
        if files:
            self.final_file_name = os.path.join(self.unique_dir, files[0])
        else:
            log("No files found in the download directory.", "ERROR")

    def set_medias_list_for_album_or_playlist(self, output):
        self.medias_list = [os.path.join(self.unique_dir, f) for f in os.listdir(self.unique_dir)]

        title_match = re.search(r'Found \d+ songs in (.*?) \(', output)
        if title_match:
            self.media_title = title_match.group(1)
        else:
            log("Could not determine the album/playlist title from the output.", "ERROR")
            if self.medias_list:
                self.media_title = os.path.basename(self.unique_dir)
            else:
                log("No files found in the download directory.", "ERROR")

    def create_zip_for_album_or_playlist(self):
        media_title = re.sub(r'[|:*?"<>\\/]', '_', self.media_title)
        file_manager = FileManager(self.medias_list, self.output_path, media_title)
        file_manager.make_archive()
        self.final_file_name = file_manager.zip_final_filename

class WebDownloader:
    def __init__(self, url, format):
        self.url = url
        self.format = format
        
        self.filename: str
        self.medias_list: list[str] = []
        self.output_path = os.path.join(os.path.dirname(__file__), 'output')

    def setup_download(self):
        log(self.url, "DEBUG")
        if 'youtube.com' in self.url or 'youtu.be' in self.url:
            web_dl = YoutubeDownloader(self.url, self.output_path, format=self.format)
            web_dl.download()
        elif 'twitter.com' in self.url or 'x.com' in self.url:
            web_dl = TwitterDownloader(self.url, self.output_path, format=self.format)
            web_dl.download()
        elif 'instagram.com' in self.url:
            web_dl = InstagramDownloader(self.url, self.output_path, format=self.format)
            web_dl.download()
        elif 'spotify.com' in self.url:
            web_dl = SpotifyDownloader(self.url, self.output_path, format=self.format)
            web_dl.download()
        else:
            return None
        self.filename = web_dl.final_file_name
        self.medias_list = web_dl.medias_list
        return True

# if __name__ == "__main__":
#     url = "https://open.spotify.com/playlist/37i9dQZF1EpiylCZQ6XZD4?si=f40e99cc1b014363" # Playlist
#     url = "https://open.spotify.com/intl-fr/album/0DsMhU0ERzMt6xvtGpgXvW?si=8UmBjpT6Qbe0STQvgKyRlg" # Album

# if __name__ == "__main__":
#     # downloader = WebDownloader("https://www.youtube.com/watch?v=icPHcK_cCF4&pp=ygUXeW91dHViZSA1IHNlY29uZHMgdmlkZW8%3D")
#     # downloader = WebDownloader("https://www.instagram.com/zurgloxleterrible/p/C61bFusC8ce/?hl=hu  ")
#     downloader = WebDownloader("https://x.com/JixonKds/status/1854489456423666137")

if __name__ == "__main__":
    WebDownloader("https://open.spotify.com/track/40EL2KYZw9V2RLdekNCQM6?si=01e5b27b43a7402e")