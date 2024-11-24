from logs import log
import subprocess, os, random, ffmpeg

class ImageToVectorConverter:
    def __init__(self, input_file):
        self.input_file = input_file

    def convert_to_vector(self, output_file, format_option):
        # Convert image to PBM format (required by Potrace)
        converter = Converter(self.input_file, 'image', 'pbm')
        if not converter.convert():
            log(f'Error converting file: {self.input_file}', "ERROR")
            return
        pbm_file = converter.output_file

        # Define format options mapping
        format_options = {
            'pdf': ['-b', 'pdf'],
            'dxf': ['-b', 'dxf'],
            'geojson': ['-b', 'geojson'],
            'pdfpage': ['-b', 'pdfpage'],
            'ps': ['-b', 'ps'],
            'pgm': ['-b', 'pgm'],
            'gimppath': ['-b', 'gimppath'],
            'xfig': ['-b', 'xfig'],
            'eps': ['-e'],
            'svg': ['-s']
        }

        # Get the Potrace arguments for the given format option
        args = format_options.get(format_option, [])
        subprocess.run(['potrace', pbm_file] + args + ['-o', output_file])

        # Clean up the intermediate PBM file
        os.remove(pbm_file)
        print(f'Converted {self.input_file} to {output_file}')

class Converter:
    def __init__(self, input_file_name, type_input_file, type_output_file):
        self.input_file_name = input_file_name
        self.type_input_file = type_input_file
        self.type_output_file = type_output_file

        self.input_file = None
        self.output_file = None
        self.output_file_name = None
        self.input_dir = os.path.join(os.path.dirname(__file__), 'uploads')
        self.output_dir = os.path.join(os.path.dirname(__file__), 'output')
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

    def get_unique_output_file(self, base_name, extension):
        output_file = os.path.join(self.output_dir, f'{base_name}_converted.{extension}')
        while os.path.exists(output_file):
            random_number = random.randint(1, 10000)
            output_file = os.path.join(self.output_dir, f'{base_name}_converted_{random_number}.{extension}')
        return output_file

    def convert(self):
        self.input_file = os.path.join(self.input_dir, f"{self.input_file_name}")
        base_name = self.input_file_name.rsplit('.', 1)[0]
        self.output_file = self.get_unique_output_file(base_name, self.type_output_file)
        self.output_file_name = os.path.basename(self.output_file)
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
            # raise Exception("An unexpected error occurred. Please try again.")

if __name__ == '__main__':
    image = ImageToVectorConverter('/home/frigiel/Documents/VSCODE/Ultimate-Converter/src/static/images/alert.png')
    image.convert_to_vector('/home/frigiel/Documents/VSCODE/Ultimate-Converter/output_vector.svg', 'svg')