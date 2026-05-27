import os
import random
import zipfile
import re
from logs import log

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
        # Sanitize media title to ensure it can be safely used in filenames
        safe_title = ''.join(c if ord(c) < 0xD800 or ord(c) > 0xDFFF else '_' for c in self.media_title)
        safe_title = re.sub(r'[|:*?"<>\\/]', '_', safe_title)
        
        # Ensure title is ASCII-compatible for zipfile
        try:
            safe_title.encode('ascii')
        except UnicodeEncodeError:
            # Replace any non-ASCII characters with underscores
            safe_title = ''.join(c if ord(c) < 128 else '_' for c in safe_title)
        
        zip_final_filename = os.path.join(self.output_path, f"{safe_title}.zip")
        while os.path.exists(zip_final_filename):
            random_number = random.randint(1, 10000)
            zip_final_filename = os.path.join(self.output_path, f"{safe_title}_{random_number}.zip")
        
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