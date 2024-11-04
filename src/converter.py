import os
import random
import ffmpeg

class Converter:
    def __init__(self, input_file_name, type_input_file, type_output_file):
        self.input_file_name = input_file_name
        self.type_input_file = type_input_file
        self.type_output_file = type_output_file

        self.input_dir = 'uploads'
        self.output_dir = 'output'
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

    def get_unique_output_file(self, base_name, extension):
        output_file = os.path.join(self.output_dir, f'{base_name}_converted.{extension}')
        while os.path.exists(output_file):
            random_number = random.randint(1, 10000)
            output_file = os.path.join(self.output_dir, f'{base_name}_converted_{random_number}.{extension}')
        return output_file

    def convert(self):
        input_file = os.path.join(self.input_dir, f"{self.input_file_name}")
        base_name = self.input_file_name.split(".")[0]
        output_file = self.get_unique_output_file(base_name, self.type_output_file)
        print(f'Converting file: {self.input_file_name} to {output_file}')
        try:
            ffmpeg.input(input_file).output(output_file).run()
            print(f'File converted successfully: {output_file}')
        except ffmpeg.Error as e:
            error_message = e.stderr.decode() if e.stderr else str(e)
            print(f'Error: {error_message}')
        except Exception as e:
            print(f'Error: {e}')
            raise Exception("An unexpected error occurred. Please try again.")

if __name__ == '__main__':
    # Example usage
    converter = Converter('example.mp4', 'video', 'png')
    converter.convert()