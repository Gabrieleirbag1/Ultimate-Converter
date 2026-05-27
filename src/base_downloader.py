import random, os, re, string
from logs import log
from converter import ClassicConverter

class BaseDownloader():
    """Base class for downloading media from the web
    
    :param str url: URL of the media to download
    :param str output_path: Path to save the downloaded media
    :param str format: Format of the downloaded media"""
    def __init__(self, url: str, output_path: str, format: str) -> None:
        self.url = url
        self.output_path = output_path
        self.format = format

        self.final_file_name: str
        self.medias_list: list[str] = []

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
        output_file = os.path.join(self.output_path, f"{base_name}.{extension}")
        while os.path.exists(output_file):
            random_number = random.randint(1, 10000)
            output_file = os.path.join(self.output_path, f"{base_name}_{random_number}.{extension}")
        return output_file

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
