import os 

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

SECRETS_PATH = os.path.join(os.path.dirname(__file__), 'secrets')


def read_secret_file(filename: str) -> dict:
    """Parse a KEY=VALUE style .secret file into a dict.

    :param str filename: name of the file inside SECRETS_PATH
    :return: dict of key/value pairs found in the file
    """
    filepath = os.path.join(SECRETS_PATH, filename)
    values = {}

    if not os.path.isfile(filepath):
        return values

    with open(filepath, 'r') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#') or '=' not in line:
                continue
            key, _, value = line.partition('=')
            values[key.strip()] = value.strip()

    return values

# Instagram
_instagram_secrets = read_secret_file('instagram.secret')
INSTAGRAM_USERNAME = _instagram_secrets.get('USERNAME')
try:
    INSTAGRAM_FILENAME = os.path.join(SECRETS_PATH, f'instaloader-session-{INSTAGRAM_USERNAME}')
except FileNotFoundError:
    INSTAGRAM_FILENAME = None

# Spotify
_spotify_secrets = read_secret_file('spotify.secret')
SPOTIFY_CLIENT_ID = _spotify_secrets.get('CLIENT_ID')
SPOTIFY_CLIENT_SECRET = _spotify_secrets.get('CLIENT_SECRET')