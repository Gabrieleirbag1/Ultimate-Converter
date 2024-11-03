import ffmpeg
import os

class Converter:
    def __init__(self, input_file, type_file1, type_file2):
        self.input_file = input_file
        self.type_file1 = type_file1
        self.type_file2 = type_file2
        self.output_dir = 'output'
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

    def convert(self):
        output_file = os.path.join(self.output_dir, f'converted.{self.type_file2}')
        print(f'Converting file: {self.input_file} to {output_file}')
        try:
            ffmpeg.input(self.input_file).output(output_file).run()
            print(f'File converted successfully: {output_file}')
        except ffmpeg.Error as e:
            print(f'Error during conversion: {e.stderr.decode()}')

# Example usage
if __name__ == '__main__':
    input_file = os.path.join(os.path.dirname(__file__), 'test.jpg')
    type_file1 = 'jpg'  # Example input type
    type_file2 = 'png'  # Example output type
    converter = Converter(input_file, type_file1, type_file2)
    converter.convert()