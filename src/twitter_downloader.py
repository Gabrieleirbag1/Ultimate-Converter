import os
import sys
import re
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm
from logs import log
from base_downloader import BaseDownloader
from youtube_downloader import YoutubeDownloader

class TwitterDownloader(BaseDownloader):
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
        super().__init__(url, output_path, format)
        self.final_file_name: str
        self.medias_list: list[str] = []

    def download(self):
        """Extract the highest quality video url to download into a file"""
        api_url = f"https://twitsave.com/info?url={self.url}"

        response = requests.get(api_url)
        data = BeautifulSoup(response.text, "html.parser")
        
        try:
            download_button = data.find_all("div", class_="origin-top-right")[0]
            quality_buttons = download_button.find_all("a")
            highest_quality_url = quality_buttons[0].get("href")  # Highest quality video url
        except (IndexError, AttributeError):
            #try download gif
            self.download_gif()
            return

        file_name = data.find_all("div", class_="leading-tight")[0].find_all("p", class_="m-2")[0].text  # Video file name
        file_name = re.sub(r"[^a-zA-Z0-9]+", ' ', file_name).strip() + f".{self.format}"  # Remove special characters from file name
        base_name = re.sub(r'[|:*?"<>\\/]', '_', file_name.rsplit('.', 1)[0])
        self.generate_file_name(base_name, "mp4")
        self.download_video(highest_quality_url, self.final_file_name)

    def download_gif(self):
        web_dl = YoutubeDownloader(self.url, self.output_path, format=self.format)
        web_dl.download()
        self.final_file_name = web_dl.final_file_name
        self.medias_list = web_dl.medias_list

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