AUDIO = ('mp3', 'aac', 'ac3', 'flac', 'wav', 'ogg', 'wma', 'aiff', 'dts', 'eac3', 'm4a', 'mp2', 'opus', 'pcm')
VIDEO = ('mp4', 'avi', 'mkv', 'mov', 'flv', 'wmv', 'mpeg', 'webm', '3gp', 'asf', 'm4v', 'ts', 'm2ts', 'vob', 'rm', 'swf')
IMAGE = ('jpeg', 'jpg', 'png', 'bmp', 'gif', 'tiff', 'webp', 'pgm', 'ppm', 'pam', 'tga')
VECTOR = ('svg', 'pdf', 'eps', 'svgz', 'dxf', 'emf', 'wmf', 'xaml', 'fxg', 'hpgl', 'odg', 'ps', 'sif')
ARCHIVE = ('7z', 'cb7', 'cbt', 'cbz', 'cpio', 'iso', 'jar', 'tar', 'tar.bz2', 'tar.gz', 'tar.lzma', 'tar.xz', 'tbz2', 'tgz', 'txz', 'zip')
ALLOWED_EXTENSIONS = AUDIO + VIDEO + IMAGE + VECTOR + ARCHIVE

AUTOTRACE_VECTOR = {
    'svg': 0, 
    'pdf': 0, 
    'fig': 2, 
    'ai': 0, 
    'sk': 0, 
    'p2e': 0, 
    'mif': 256, 
    'er': 0, 
    'eps': 0, 
    'emf': 0, 
    'dxf': 0, 
    'drd2': 0, 
    'cgm': 0
}

FORMATS = {
    'audio': AUDIO,
    'video': VIDEO,
    'image': IMAGE,
    'vector': tuple(VECTOR) + tuple(AUTOTRACE_VECTOR.keys()),
    'archive': ARCHIVE
}
