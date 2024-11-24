from PIL import Image
import subprocess
import os

class ImageToVectorConverter:
    def __init__(self, input_file):
        self.input_file = input_file

    def convert_to_vector(self, output_file, format_option):
        # Convert image to PBM format (required by Potrace)
        image = Image.open(self.input_file).convert('1')
        pbm_file = self.input_file.replace('.png', '.pbm')
        image.save(pbm_file)

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

if __name__ == '__main__':
    input_file = '/home/frigiel/Documents/VSCODE/Ultimate-Converter/src/static/images/alert.png'  # Replace with your input image file

    converter = ImageToVectorConverter(input_file)

    # Convert to different vector formats
    converter.convert_to_vector('/home/frigiel/Documents/VSCODE/Ultimate-Converter/output_vector.eps', 'eps')
    converter.convert_to_vector('/home/frigiel/Documents/VSCODE/Ultimate-Converter/output_vector.pdf', 'pdf')
    converter.convert_to_vector('/home/frigiel/Documents/VSCODE/Ultimate-Converter/output_vector.svg', 'svg')
    converter.convert_to_vector('/home/frigiel/Documents/VSCODE/Ultimate-Converter/output_vector.dxf', 'dxf')
    converter.convert_to_vector('/home/frigiel/Documents/VSCODE/Ultimate-Converter/output_vector.geojson', 'geojson')
    converter.convert_to_vector('/home/frigiel/Documents/VSCODE/Ultimate-Converter/output_vector.pdfpage', 'pdfpage')
    converter.convert_to_vector('/home/frigiel/Documents/VSCODE/Ultimate-Converter/output_vector.ps', 'ps')
    converter.convert_to_vector('/home/frigiel/Documents/VSCODE/Ultimate-Converter/output_vector.pgm', 'pgm')
    converter.convert_to_vector('/home/frigiel/Documents/VSCODE/Ultimate-Converter/output_vector.gimppath', 'gimppath')
    converter.convert_to_vector('/home/frigiel/Documents/VSCODE/Ultimate-Converter/output_vector.xfig', 'xfig')