from instaloader import Post, Instaloader
from logs import log
from base_downloader import BaseDownloader

class InstagramDownloader(BaseDownloader):
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
        super().__init__(url, output_path, format)

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

    def download_video(self, post: Post):
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