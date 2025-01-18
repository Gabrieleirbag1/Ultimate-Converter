from shutil import rmtree
import subprocess, os, random, ffmpeg, patoolib

from utils import IMAGE, VIDEO, VECTOR, ARCHIVE, AUTOTRACE_VECTOR
from logs import log

class BaseConverter:
    def __init__(self, input_file_name: str, type_output_file: str):
        self.input_file_name = input_file_name
        self.type_output_file = type_output_file

        self.input_dir = os.path.join(os.path.dirname(__file__), 'uploads')
        self.output_dir = os.path.join(os.path.dirname(__file__), 'output')
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
        self.setup_files()

    def setup_files(self):
        self.input_file = os.path.join(self.input_dir, f"{self.input_file_name}")
        base_name = self.input_file_name.rsplit('.', 1)[0]
        self.output_file = self.get_unique_output_file(base_name, self.type_output_file)
        self.output_file_name = os.path.basename(self.output_file)

    def get_unique_output_file(self, base_name, extension):
        output_file = os.path.join(self.output_dir, f'{base_name}_converted.{extension}')
        while os.path.exists(output_file):
            random_number = random.randint(1, 10000)
            output_file = os.path.join(self.output_dir, f'{base_name}_converted_{random_number}.{extension}')
        return output_file

class ArchiveConverter(BaseConverter):
    def __init__(self, input_file_name: str, type_output_file: str):
        super().__init__(input_file_name, type_output_file)

    def convert(self):
        try:
            unique_dir = os.path.join(self.output_dir, self.get_unique_output_file(self.input_file_name, 'dir'))
            os.makedirs(unique_dir, exist_ok=True)
            patoolib.extract_archive(self.input_file, outdir=unique_dir)
            # Change the working directory to the unique directory
            cwd = os.getcwd()
            os.chdir(unique_dir)
            # Create the output archive without including the full path
            patoolib.create_archive(self.output_file, ('.',))
            # Change back to the original working directory
            os.chdir(cwd)
            rmtree(unique_dir)
            log(f"Converted {self.input_file_name} to {self.output_file_name}", "INFO")
            return True
        except patoolib.util.PatoolError as e:
            log(f"Error extracting archive: {str(e)}", "ERROR")
            return False
        except Exception as e:
            log(f"An error occurred: {str(e)}", "ERROR")
            log(f"Line: {e.__traceback__.tb_lineno}", "ERROR")
            return False

class ImageToVectorConverter(BaseConverter):
    def __init__(self, input_file_name: str, type_output_file: str):
        super().__init__(input_file_name, type_output_file)
        # self.format_options = {
        #     'pdf': ['-b', 'pdf'],
        #     'dxf': ['-b', 'dxf'],
        #     'geojson': ['-b', 'geojson'],
        #     'pdfpage': ['-b', 'pdfpage'],
        #     'ps': ['-b', 'ps'],
        #     'pgm': ['-b', 'pgm'],
        #     'gimppath': ['-b', 'gimppath'],
        #     'xfig': ['-b', 'xfig'],
        #     'eps': ['-e'],
        #     'svg': ['-s']
        # }

    def convert(self):        
        converter = ClassicConverter(self.input_file, 'bmp')
        if not converter.convert():
            log(f'Error converting file: {self.input_file}', "ERROR")
            return False
        
        bmp_file = converter.output_file

        try:
            # args = self.format_options.get(self.type_output_file, [])
            # subprocess.run(['potrace', bmp_file] + args + ['-o', self.output_file])
            subprocess.run(['docker', 'run', '--rm', '-v', f"{os.getcwd()}:{os.getcwd()}", '-w', os.getcwd(), 'autotrace', '-preserve-width', '-color-count', str(AUTOTRACE_VECTOR[self.type_output_file]), bmp_file, '-output-file', self.output_file, '-output-format', self.type_output_file])
            os.remove(bmp_file)
            log(f'Converted {self.input_file} to {self.output_file}', "DEBUG")
            return True
        except subprocess.CalledProcessError as e:
            log(f'Error during subprocess execution: {e}', "ERROR")
            return False
        except Exception as e:
            log(f'An unexpected error occurred during conversion: {str(e)}', "ERROR")
            return False
    
class VectorConverter(BaseConverter):
    def __init__(self, input_file_name: str, type_output_file: str, type_input_file: str):
        self.original_type_output_file = type_output_file
        self.type_input_file = type_input_file
        type_output_file = self.check_format(type_output_file)
        super().__init__(input_file_name, type_output_file)

    def check_format(self, type_output_file):
        if type_output_file in IMAGE and type_output_file != "png":
            return "png"
        return type_output_file

    def convert_to_png(self):
        png_output_file = self.get_unique_output_file(self.input_file_name.rsplit('.', 1)[0], 'png')
        try:
            ffmpeg.input(self.input_file).output(png_output_file).run(capture_stdout=True, capture_stderr=True)
            self.input_file = png_output_file
        except ffmpeg.Error as e:
            error_message = e.stderr.decode() if e.stderr else str(e)
            log(f'Error converting file to PNG: {error_message}', "ERROR")
            raise

    def convert(self):
        try:
            if self.type_input_file in IMAGE and not self.input_file.endswith('.png'):
                self.convert_to_png()
            subprocess.run(['docker', 'exec', 'inkscape', 'inkscape', self.input_file, '--export-type=' + self.type_output_file, '--export-filename=' + self.output_file], check=True)
            if self.original_type_output_file != self.type_output_file:
                converter = ClassicConverter(self.output_file, self.original_type_output_file)
                if not converter.convert():
                    log(f'Error converting file: {self.output_file}', "ERROR")
                    return False
                self.output_file = converter.output_file
            return True
        except subprocess.CalledProcessError as e:
            log(f'Error during subprocess execution: {e}', "ERROR")
            return False
        except Exception as e:
            log(f'An unexpected error occurred during conversion: {str(e)}', "ERROR")
            return False
    
class ClassicConverter(BaseConverter):
    def __init__(self, input_file_name, type_output_file):
        super().__init__(input_file_name, type_output_file)

    def convert(self):
        try:
            if self.type_output_file == 'rm':
                width, height = self.convert_16bit(16)
                ffmpeg.input(self.input_file).output(self.output_file, vf=f'scale={width}:{height}', strict='-2').run(capture_stdout=True, capture_stderr=True)
            elif self.type_output_file in IMAGE and self.input_file.endswith('.gif'):
                ffmpeg.input(self.input_file).output(self.output_file, vframes=1).run(capture_stdout=True, capture_stderr=True)
            else:
                ffmpeg.input(self.input_file).output(self.output_file, strict='-2').run(capture_stdout=True, capture_stderr=True)
            log(f'File converted successfully: {self.output_file_name}', "INFO")
            return True
        except ffmpeg.Error as e:
            error_message = e.stderr.decode() if e.stderr else str(e)
            log(f'Error converting file: {error_message}', "ERROR")
            return False
        except Exception as e:
            log(f'An unexpected error occurred: {str(e)}', "ERROR")
            return False
        
    def convert_xbit(self, x):
        probe = ffmpeg.probe(self.input_file)
        video_stream = next((stream for stream in probe['streams'] if stream['codec_type'] == 'video'), None)
        width = int(video_stream['width'])
        height = int(video_stream['height'])
        if width % x != 0:
            width = (width // x) * x
        if height % x != 0:
            height = (height // x) * x
        return width, height
class ManageConversion:
    def __init__(self, input_file_name, type_output_file, type_input_file):
        self.input_file_name = input_file_name
        self.type_output_file = type_output_file
        self.type_input_file = type_input_file

        self.converter = None
        self.convert()

    def convert(self):
        if "(autotrace)" in self.type_output_file:
            type_output_file = self.type_output_file.replace(" (autotrace)", "")
            self.converter = ImageToVectorConverter(self.input_file_name, type_output_file)
        elif self.type_input_file in VECTOR or self.type_output_file in VECTOR:
            self.converter = VectorConverter(self.input_file_name, self.type_output_file, self.type_input_file)
        elif os.path.basename(self.type_input_file) in ARCHIVE or self.type_output_file in ARCHIVE:
            self.converter = ArchiveConverter(self.input_file_name, self.type_output_file)
        else:
            self.converter = ClassicConverter(self.input_file_name, self.type_output_file)