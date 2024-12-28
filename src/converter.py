from logs import log
import subprocess, os, random, ffmpeg, patoolib

VECTOR = {'svg': 0, 'pdf': 0, 'fig': 2, 'ai': 0, 'sk': 0, 'p2e': 0, 'mif': 256, 'er': 0, 'eps': 0, 'emf': 0, 'dxf': 0, 'drd2': 0, 'cgm': 0}
ARCHIVE = ('7z', 'cb7', 'cbt', 'cbz', 'cpio', 'iso', 'jar', 'tar', 'tar.bz2', 'tar.gz', 'tar.lzma', 'tar.xz', 'tbz2', 'tgz', 'txz', 'zip')

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
            for root, dirs, files in os.walk(unique_dir, topdown=False):
                for name in files:
                    os.remove(os.path.join(root, name))
                for name in dirs:
                    os.rmdir(os.path.join(root, name))
            os.rmdir(unique_dir)
            log(f"Converted {self.input_file_name} to {self.output_file_name}", "INFO")
            return True
        except Exception as e:
            log(f"An error occurred: {str(e)}", "ERROR")
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
            subprocess.run(['docker', 'run', '--rm', '-v', f"{os.getcwd()}:{os.getcwd()}", '-w', os.getcwd(), 'autotrace', '-preserve-width', '-color-count', str(VECTOR[self.type_output_file]), bmp_file, '-output-file', self.output_file, '-output-format', self.type_output_file])
            os.remove(bmp_file)
            log(f'Converted {self.input_file} to {self.output_file}', "DEBUG")
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
        print(f'Converting file: {self.input_file_name} to {self.output_file}')
        try:
            ffmpeg.input(self.input_file).output(self.output_file).run(capture_stdout=True, capture_stderr=True)
            log(f'File converted successfully: {self.output_file_name}', "INFO")
            return True
        except ffmpeg.Error as e:
            error_message = e.stderr.decode() if e.stderr else str(e)
            log(f'Error converting file: {error_message}', "ERROR")
            return False
        except Exception as e:
            log(f'An unexpected error occurred: {str(e)}', "ERROR")
            return False
        
class ManageConversion:
    def __init__(self, input_file_name, type_output_file, type_input_file):
        self.input_file_name = input_file_name
        self.type_output_file = type_output_file
        self.type_input_file = type_input_file

        self.converter = None
        self.convert()

    def convert(self):
        if self.type_input_file.split("/")[1] in VECTOR.keys() or self.type_output_file in VECTOR.keys():
            self.converter = ImageToVectorConverter(self.input_file_name, self.type_output_file)
        elif self.type_input_file.split("/")[1] in ARCHIVE or self.type_output_file in ARCHIVE:
            self.converter = ArchiveConverter(self.input_file_name, self.type_output_file)
        else:
            self.converter = ClassicConverter(self.input_file_name, self.type_output_file)

if __name__ == '__main__':
    convert_zip = ManageConversion('/home/frigiel/Téléchargements/test.zip', 'tar', 'application/zip')
    convert_zip.converter.convert()