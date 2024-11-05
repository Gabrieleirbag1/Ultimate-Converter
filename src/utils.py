from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
app.config['UPLOADED_FILES_DEST'] = os.path.join(app.root_path, 'uploads')
app.config['OUTPUT_FILES_DEST'] = os.path.join(app.root_path, 'output')
app.config['MAX_CONTENT_LENGTH'] = 250 * 1024 * 1024
app.secret_key = 'supersecretkey'

db = SQLAlchemy(app)

AUDIO = ('mp3', 'aac', 'ac3', 'flac', 'wav', 'ogg', 'wma', 'alac', 'aiff', 'amr', 'dts', 'eac3', 'm4a', 'mp2', 'opus', 'pcm', 'vorbis')
VIDEO = ('mp4', 'avi', 'mkv', 'mov', 'flv', 'wmv', 'mpeg', 'webm', '3gp', 'asf', 'm4v', 'ts', 'm2ts', 'vob', 'rm', 'swf')
IMAGE = ('jpeg', 'jpg', 'png', 'bmp', 'gif', 'tiff', 'webp', 'pgm', 'ppm', 'pam', 'pnm', 'tga')
VECTOR = ('svg', 'eps', 'pdf', 'ai', 'emf', 'wmf')
SUBTITLE = ('srt', 'ass', 'ssa', 'sub', 'vtt', 'stl', 'dfxp', 'sami', 'mpl2', 'pjs', 'jacosub')
ARCHIVE = ('tar', 'zip', 'gz', 'bz2', 'rar', '7z')

ALLOWED_EXTENSIONS = AUDIO + VIDEO + IMAGE + SUBTITLE + ARCHIVE