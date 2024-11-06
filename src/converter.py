import os
import random
import ffmpeg
from logs import log

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
        base_name = self.input_file_name.split(".")[0]
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
    # Example usage
    converter = Converter('example.mp4', 'video', 'png')
    converter.convert()