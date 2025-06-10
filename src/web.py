from instaloader import Post, Instaloader
import random, os, re, sys, requests, subprocess, string, zipfile, uuid, time
from bs4 import BeautifulSoup
from tqdm import tqdm
from logs import log
from converter import ClassicConverter
from yt_dlp import YoutubeDL

class FileManager:
    """Class to manage the files downloaded from the web

    :param list[str] media_files: List of media files to archive
    :param str output_path: Path to save the archive
    :param str media_title: Title of the media files
    :param str zip_final_filename: Final name of the zip file
    """    
    def __init__(self, media_files: list[str], output_path: str, media_title: str):
        """Initialize the FileManager class
        
        :param list[str] media_files: List of media files to archive
        :param str output_path: Path to save the archive
        :param str media_title: Title of the media files
        """
        self.media_files = media_files
        self.output_path = output_path
        self.media_title = media_title

        self.zip_final_filename: str

    def get_unique_output_file(self):
        """Get a unique name for the output zip file"""
        zip_final_filename = os.path.join(self.output_path, f"{self.media_title}.zip")
        while os.path.exists(zip_final_filename):
            random_number = random.randint(1, 10000)
            zip_final_filename = os.path.join(self.output_path, f"{self.media_title}_{random_number}.zip")
        self.zip_final_filename = zip_final_filename

    def remove_uploaded_file(self, file_path: str):
        """Remove the uploaded file after archiving
        
        :param str file_path: Path to the file to remove"""
        try:
            os.remove(file_path)
        except FileNotFoundError:
            pass

    def make_archive(self):
        """Create a zip archive of the media files"""
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
    """Class to download youtube videos and playlists
    
    :param str url: URL of the youtube video or playlist
    :param str output_path: Path to save the downloaded media
    :param str quality: Quality of the video
    :param str media: Type of media to download
    :param str format: Format to convert the media to
    :param str final_file_name: Final name of the downloaded file
    :param list[str] medias_list: List of media files downloaded in a playlist
    """
    def __init__(self, url: str, output_path: str, quality: str ='highest', media: str ='video', format: str ='mp4') -> None:
        """Initialize the YoutubeDownloader class
        
        :param str url: URL of the youtube video or playlist
        :param str output_path: Path to save the downloaded media
        :param str quality: Quality of the video
        :param str media: Type of media to download
        :param str format: Format to convert the media to
        
        :return: None"""
        super().__init__()
        self.url = url
        self.output_path = output_path
        self.quality = quality
        self.media = media
        self.format = format

        self.final_file_name: str
        self.medias_list: list[str] = []

    def download(self):
        """Download the youtube video or playlist"""
        if 'playlist' in self.url:
            self.download_playlist()
        else:
            self.download_video()

    def convert_file(self, extension: str):
        """Convert the downloaded file to a different format

        :param str extension: Extension of the downloaded file"""
        file_path = os.path.join(self.output_path, self.final_file_name)
        if self.format != extension:
            converter = ClassicConverter(file_path, self.format)
            if not converter.convert():
                log(f"Error converting file: {self.final_file_name}", "ERROR")
            if os.path.exists(self.final_file_name):
                os.remove(self.final_file_name)
            self.final_file_name = converter.output_file

    def download_video(self):
        """Download a single youtube video"""
        timestamp = time.strftime("%Y%m%d-%H%M%S")
        ydl_opts = {
            'format': 'bestvideo+bestaudio/best',
            'outtmpl': os.path.join(self.output_path, f'%(title)s_{timestamp}.%(ext)s'),
        }

        with YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(self.url, download=True)
            self.final_file_name = ydl.prepare_filename(info_dict)
            yt_dl_extension = os.path.basename(self.final_file_name.rsplit('.', 1)[1])
            self.final_file_name = self.final_file_name.replace("webm", yt_dl_extension)

        self.convert_file(yt_dl_extension)
        log(f"Downloaded {self.final_file_name} in {self.media} media with {self.quality} quality", "INFO")

    def download_playlist(self):
        """Download a youtube playlist"""
        timestamp = time.strftime("%Y%m%d-%H%M%S")
        ydl_opts = {
            'format': 'bestvideo+bestaudio/best',
            'outtmpl': os.path.join(self.output_path, f'%(playlist)s_{timestamp}/%(title)s.%(ext)s'),
        }

        with YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(self.url, download=True)
            for entry in info_dict['entries']:
                log(f"Downloading {entry['title']}", "INFO")
                self.final_file_name = ydl.prepare_filename(entry)
                yt_dl_extension = os.path.basename(self.final_file_name.rsplit('.', 1)[1])
                log('File name: ' + self.final_file_name, "DEBUG")
                self.final_file_name = self.final_file_name.replace("webm", yt_dl_extension)
                log(f"Extension: {yt_dl_extension}", "DEBUG")
                log(f"Final file name: {self.final_file_name}", "DEBUG")
                self.convert_file(yt_dl_extension)
                self.medias_list.append(self.final_file_name)
                log(self.medias_list, "DEBUG")
        
        playlist_title = re.sub(r'[|:*?"<>\\/]', '_', info_dict['title'])
        file_manager = FileManager(self.medias_list, self.output_path, playlist_title)
        file_manager.make_archive()
        self.final_file_name = file_manager.zip_final_filename
        playlist_dir = os.path.join(self.output_path, f"{playlist_title}_{timestamp}")
        if os.path.exists(playlist_dir):
            os.rmdir(playlist_dir)
        log(f"Downloaded playlist: {info_dict['title']}", "INFO")

class InstagramDownloader:
    """Class to download instagram posts
    
    :param str url: URL of the instagram post
    :param str output_path: Path to save the downloaded media
    :param str format: Format to convert the media to
    :param str final_file_name: Final name of the downloaded file
    :param list[str] medias_list: List of media files downloaded in a playlist
    """
    def __init__(self, url: str, output_path: str, format: str ='mp4') -> None:
        """Initialize the InstagramDownloader class
        
        :param str url: URL of the instagram post
        :param str output_path: Path to save the downloaded media
        :param str format: Format to convert the media to
        
        :return: None"""
        self.url = url
        self.output_path = output_path
        self.format = format
        self.loader = Instaloader()

        self.final_file_name: str
        self.medias_list: list[str] = []

    def download(self):
        """Download the instagram post"""
        post = Post.from_shortcode(self.loader.context, self.url.split('/')[-2])
        if post.is_video:
            self.download_video(post)
        else:
            self.download_image(post)
        
    def convert_file(self, extension: str):
        """Convert the downloaded file to a different format
        
        :param str extension: Extension of the downloaded file"""
        if self.format != extension:
            converter = ClassicConverter(self.final_file_name, self.format)
            if not converter.convert():
                log(f"Error converting file: {self.final_file_name}", "ERROR")
            if os.path.exists(self.final_file_name):
                os.remove(self.final_file_name)
            self.final_file_name = converter.output_file

    def download_video(self, post: str):
        """Download the video from the instagram post
        
        :param Post post: The instagram post object"""
        if self.format not in ['mp4', 'webm']:
            log(f"Format {self.format} not supported for videos. Defaulting to mp4.", "WARNING")
            extension = 'mp4'
        else:
            extension = self.format
        video_url = post.video_url
        self.download_file(video_url, post, extension)

    def download_image(self, post: Post):
        """Download the image from the instagram post
        
        :param Post post: The instagram post object"""
        if self.format not in ['jpg', 'png']:
            log(f"Format {self.format} not supported for images. Defaulting to jpg.", "WARNING")
            extension = 'jpg'
        else:
            extension = self.format
        image_url = post.url
        self.download_file(image_url, post, extension)

    def generate_file_name(self, file_name: str, extension: str):
        """Generate a unique file name for the downloaded media
        
        :param str file_name: Name of the media file
        :param str extension: Extension of the media file"""
        base_name = re.sub(r'[|:*?"<>\\/]', '_', file_name.rsplit('.', 1)[0])
        log(f"Base name: {base_name}", "DEBUG")
        if str.isspace(base_name) or not base_name:
            base_name = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
        if len(base_name) > 50:
            base_name = base_name[:50]
        self.final_file_name = self.get_unique_output_file(base_name, extension)

    def download_file(self, file_url: str, post: Post, extension: str):
        """Download the media file from the URL
        
        :param str file_url: URL of the media file
        :param Post post: The instagram post object
        :param str extension: Extension of the media file"""
        file_name = post.shortcode
        self.generate_file_name(file_name, extension)
        log(f"Downloading {self.final_file_name} from {file_url}", "INFO")
        self.loader.download_pic(self.final_file_name.rsplit(".", 1)[0], file_url, post.date_utc)
        self.convert_file(extension)

    def get_unique_output_file(self, base_name: str, extension: str) -> str:
        """Get a unique name for the output file
        
        :param str base_name: Base name of the file
        :param str extension: Extension of the file
        
        :return: Unique name for the output file
        :rtype: str"""
        output_file = os.path.join(self.output_path, f'{base_name}_converted.{extension}')
        while os.path.exists(output_file):
            random_number = random.randint(1, 10000)
            output_file = os.path.join(self.output_path, f'{base_name}_converted_{random_number}.{extension}')
        return output_file

class TwitterDownloader:
    """Class to download twitter videos
    
    :param str url: URL of the twitter post
    :param str output_path: Path to save the downloaded media
    :param str format: Format to convert the media to
    :param str final_file_name: Final name of the downloaded file
    :param list[str] medias_list: List of media files downloaded in a playlist
    """
    def __init__(self, url: str, output_path: str, format: str = "mp4") -> None:
        """Initialize the TwitterDownloader class
        
        :param str url: URL of the twitter post
        :param str output_path: Path to save the downloaded media
        :param str format: Format to convert the media to
        
        :return: None"""
        self.url = url
        self.output_path = output_path
        self.format = format

        self.final_file_name: str
        self.medias_list: list[str] = []

    def download(self):
        """Extract the highest quality video url to download into a file"""
        api_url = f"https://twitsave.com/info?url={self.url}"

        response = requests.get(api_url)
        data = BeautifulSoup(response.text, "html.parser")
        download_button = data.find_all("div", class_="origin-top-right")[0]
        quality_buttons = download_button.find_all("a")
        highest_quality_url = quality_buttons[0].get("href")  # Highest quality video url

        self.generate_file_name(data)
        self.download_video(highest_quality_url, self.final_file_name)

    def convert_file(self, extension: str):
        """Convert the downloaded file to a different format
        
        :param str extension: Extension of the downloaded file"""
        if self.format != extension:
            converter = ClassicConverter(self.final_file_name, self.format)
            if not converter.convert():
                log(f"Error converting file: {self.final_file_name}", "ERROR")
            if os.path.exists(self.final_file_name):
                os.remove(self.final_file_name)
            self.final_file_name = converter.output_file

    def get_unique_output_file(self, base_name: str, extension: str) -> str:
        """Get a unique name for the output file
        
        :param str base_name: Base name of the file
        :param str extension: Extension of the file
        
        :return: Unique name for the output file
        :rtype: str"""
        output_file = os.path.join(self.output_path, f'{base_name}.{extension}')
        while os.path.exists(output_file):
            random_number = random.randint(1, 10000)
            output_file = os.path.join(self.output_path, f'{base_name}_{random_number}.{extension}')
        return output_file

    def download_video(self, url: str, file_name: str):
        """Download a video from a URL into a filename.

        :param str url: URL of the video
        :param str file_name: Name of the file
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

    def generate_file_name(self, data: str):
        """Generate a unique file name for the downloaded media
        
        :param str data: Data from the twitter post"""
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
        """Check if the URL is a valid Twitter video URL"""
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
        self.bitrate = "320k"

    def download(self):
        self.check_spotify_type()
        self.create_unique_directory()
        script_dir_name = os.path.dirname(os.path.realpath(__file__))
        command = [
            'docker', 'run', '--rm', 
            '-v', f"{script_dir_name}:{script_dir_name}", 
            '-w', script_dir_name, 
            'spotdl',
            'download',
            self.url,
            '--output', self.unique_dir,
            '--bitrate', self.bitrate,
            '--format', 'mp3'
        ]
        
        try:
            # Use bytes mode instead of text mode to avoid encoding issues
            result = subprocess.run(command, check=True, capture_output=True, text=False)
            log(f"Downloaded successfully to {self.unique_dir}", "INFO")
            
            # Safely decode output with error handling
            output = result.stdout.decode('utf-8', errors='replace')
            log(output, "DEBUG")
            
            if self.type == 'track':
                self.set_final_file_name_for_track()
                self.convert_file(self.final_file_name, "mp3")
            else:
                self.set_medias_list_for_album_or_playlist(output)
                self.create_zip_for_album_or_playlist()
                self.remove_unique_directory()
        except subprocess.CalledProcessError as e:
            log(f"Error during download: {e}", "ERROR")
            # Safely decode stderr with error handling
            stderr_output = e.stderr.decode('utf-8', errors='replace') if e.stderr else "No stderr output"
            log(f"Error output: {stderr_output}", "ERROR")

    def convert_file(self, file_path, extension):
        if self.format != extension:
            converter = ClassicConverter(file_path, self.format)
            if not converter.convert():
                log(f"Error converting file: {file_path}", "ERROR")
            if os.path.exists(file_path):
                os.remove(file_path)
            return converter.output_file
        return file_path

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

    def set_final_file_name_for_track(self):
        files = os.listdir(self.unique_dir)
        if files:
            self.final_file_name = os.path.join(self.unique_dir, files[0])
            log(f"Final file name: {self.final_file_name}", "WARNING")
        else:
            log("No files found in the download directory.", "ERROR")

    def set_medias_list_for_album_or_playlist(self, output):
        self.medias_list = []
        for file in os.listdir(self.unique_dir):
            # Clean the filename before processing
            clean_file = file
            try:
                # Test if the filename can be properly encoded
                clean_file.encode('utf-8')
            except UnicodeEncodeError:
                # Replace problematic characters in the filename
                clean_file = ''.join(c if ord(c) < 0xD800 or ord(c) > 0xDFFF else '_' for c in file)
                old_path = os.path.join(self.unique_dir, file)
                new_path = os.path.join(self.unique_dir, clean_file)
                os.rename(old_path, new_path)
                log(f"Renamed file with problematic characters: {file} -> {clean_file}", "WARNING")
                file = clean_file
            
            file_path = os.path.join(self.unique_dir, file)
            converted_file_path = self.convert_file(file_path, "mp3")
            self.medias_list.append(converted_file_path)

        title_match = re.search(r'Found \d+ songs in (.*?) \(', output)
        if title_match:
            self.media_title = title_match.group(1)
            # Clean media title of any problematic characters
            self.media_title = ''.join(c if ord(c) < 0xD800 or ord(c) > 0xDFFF else '_' for c in self.media_title)
        else:
            log("Could not determine the album/playlist title from the output.", "ERROR")
            if self.medias_list:
                self.media_title = os.path.basename(self.unique_dir)
            else:
                log("No files found in the download directory.", "ERROR")

    def create_zip_for_album_or_playlist(self):
        # Clean media title of special characters and surrogate pairs
        media_title = ''.join(c if ord(c) < 0xD800 or ord(c) > 0xDFFF else '_' for c in self.media_title)
        media_title = re.sub(r'[|:*?"<>\\/]', '_', media_title)
        
        try:
            file_manager = FileManager(self.medias_list, self.output_path, media_title)
            file_manager.make_archive()
            self.final_file_name = file_manager.zip_final_filename
        except UnicodeEncodeError as e:
            log(f"Unicode error during zip creation: {e}", "ERROR")
            # Create a clean list with safe filenames
            clean_medias_list = []
            for file_path in self.medias_list:
                try:
                    # Test if the path can be properly encoded
                    file_path.encode('utf-8')
                    clean_medias_list.append(file_path)
                except UnicodeEncodeError:
                    # Create a clean copy with a safe name
                    dir_name = os.path.dirname(file_path)
                    base_name = os.path.basename(file_path)
                    clean_name = ''.join(c if ord(c) < 0xD800 or ord(c) > 0xDFFF else '_' for c in base_name)
                    new_path = os.path.join(dir_name, clean_name)
                    os.rename(file_path, new_path)
                    clean_medias_list.append(new_path)
                    log(f"Renamed file for zip: {base_name} -> {clean_name}", "WARNING")
            
            # Try again with clean list
            file_manager = FileManager(clean_medias_list, self.output_path, media_title)
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