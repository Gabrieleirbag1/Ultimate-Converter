import os
import subprocess
import uuid
import re
from logs import log
from converter import ClassicConverter
from file_manager import FileManager
from utils import SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET

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
            '--format', 'mp3',
            '--client-id', SPOTIFY_CLIENT_ID,
            '--client-secret', SPOTIFY_CLIENT_SECRET
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
                self.final_file_name = self.convert_file(self.final_file_name, os.path.basename(self.final_file_name.rsplit('.', 1)[1]))
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