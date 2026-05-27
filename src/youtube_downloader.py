import os
import time
import re
from yt_dlp import YoutubeDL
from logs import log
from converter import ClassicConverter
from base_downloader import BaseDownloader
from file_manager import FileManager

class YoutubeDownloader(BaseDownloader):
    """Class to download youtube videos and playlists
    
    :param str url: URL of the youtube video or playlist
    :param str output_path: Path to save the downloaded media
    :param str quality: Quality of the video
    :param str media: Type of media to download
    :param str format: Format to convert the media to
    :param str final_file_name: Final name of the downloaded file
    :param list[str] medias_list: List of media files downloaded in a playlist
    """
    def __init__(self, url: str, output_path: str, quality: str ='highest', media: str ='video', format: str ='mp4', resolution: str ='best', codec: str ='best') -> None:
        """Initialize the YoutubeDownloader class
        
        :param str url: URL of the youtube video or playlist
        :param str output_path: Path to save the downloaded media
        :param str quality: Quality of the video
        :param str media: Type of media to download
        :param str format: Format to convert the media to
        :param str resolution: Resolution of the video
        :param str codec: Codec of the video
        
        :return: None"""
        super().__init__(url, output_path, format)
        self.quality = quality
        self.media = media
        self.resolution = resolution
        self.codec = codec

        self.final_file_name: str
        self.medias_list: list[str] = []

    def get_yt_dlp_format(self) -> str:
        """Generate yt-dlp format string based on user parameters"""
        video_format = 'bestvideo'
        
        if hasattr(self, 'resolution') and self.resolution != 'best':
            video_format += f"[height<={self.resolution}]"
        
        if hasattr(self, 'codec') and self.codec != 'best':
            video_format += f"[vcodec^={self.codec}]"
            
        return f"{video_format}+bestaudio/best"

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
        if self.format != extension or 'tiktok.com' in self.url:
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
            'format': self.get_yt_dlp_format(),
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
            'format': self.get_yt_dlp_format(),
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