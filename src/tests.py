AUDIO = ('mp3', 'aac', 'ac3', 'flac', 'wav', 'ogg', 'wma', 'alac', 'aiff', 'amr', 'dts', 'eac3', 'm4a', 'mp2', 'opus', 'pcm', 'vorbis')
VIDEO = ('mp4', 'avi', 'mkv', 'mov', 'flv', 'wmv', 'mpeg', 'webm', '3gp', 'asf', 'm4v', 'ts', 'm2ts', 'vob', 'rm', 'swf')
IMAGE = ('jpeg', 'jpg', 'png', 'bmp', 'gif', 'tiff', 'webp', 'pgm', 'ppm', 'pam', 'pnm', 'tga')
VECTOR = {'svg': 0, 'pdf': 0, 'fig': 2, 'ai': 0, 'sk': 0, 'p2e': 0, 'mif': 256, 'er': 0, 'eps': 0, 'emf': 0, 'dxf': 0, 'drd2': 0, 'cgm': 0}
ARCHIVE = ('7z', 'cb7', 'cbt', 'cbz', 'cpio', 'iso', 'jar', 'tar', 'tar.bz2', 'tar.gz', 'tar.lzma', 'tar.xz', 'tbz2', 'tgz', 'txz', 'zip')

FORMATS = {'audio': AUDIO, 'video': VIDEO, 'image': IMAGE, 'vector': VECTOR, 'archive': ARCHIVE}

test = "svg"

def get_format_category(extension):
    for category, extensions in FORMATS.items():
        if extension in extensions:
            return category
    return None

category = get_format_category(test)
print(f"The category for the extension '{test}' is: {category}")