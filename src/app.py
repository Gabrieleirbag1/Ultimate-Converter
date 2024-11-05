from flask import Flask, render_template, request, redirect, url_for, flash, send_file, get_flashed_messages
from flask_uploads import UploadSet, UploadNotAllowed, configure_uploads
from db import db
from converter import Converter
from models import Media, DownloadToken
from datetime import datetime, timedelta
import uuid, os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
app.config['UPLOADED_FILES_DEST'] = os.path.join(app.root_path, 'uploads')
app.config['OUTPUT_FILES_DEST'] = os.path.join(app.root_path, 'output')
app.config['MAX_CONTENT_LENGTH'] = 250 * 1024 * 1024
app.secret_key = 'supersecretkey'

db.init_app(app)

AUDIO = ('mp3', 'aac', 'ac3', 'flac', 'wav', 'ogg', 'wma', 'alac', 'aiff', 'amr', 'dts', 'eac3', 'm4a', 'mp2', 'opus', 'pcm', 'vorbis')
VIDEO = ('mp4', 'avi', 'mkv', 'mov', 'flv', 'wmv', 'mpeg', 'webm', '3gp', 'asf', 'm4v', 'ts', 'm2ts', 'vob', 'rm', 'swf')
IMAGE = ('jpeg', 'jpg', 'png', 'bmp', 'gif', 'tiff', 'webp', 'pgm', 'ppm', 'pam', 'pnm', 'tga')
VECTOR = ('svg', 'eps', 'pdf', 'ai', 'emf', 'wmf')
SUBTITLE = ('srt', 'ass', 'ssa', 'sub', 'vtt', 'stl', 'dfxp', 'sami', 'mpl2', 'pjs', 'jacosub')
ARCHIVE = ('tar', 'zip', 'gz', 'bz2', 'rar', '7z')

ALLOWED_EXTENSIONS = AUDIO + VIDEO + IMAGE + SUBTITLE + ARCHIVE

files = UploadSet('files', ALLOWED_EXTENSIONS)
configure_uploads(app, files)

def create_media(filename, filetype, filepath):
    print(f'Creating media: {filename}')
    media = Media(filename=filename, filetype=filetype, filepath=filepath)
    db.session.add(media)
    db.session.commit()

def create_token(converter: Converter) -> str:
    token = str(uuid.uuid4())
    expires_at = datetime.now() + timedelta(hours=1)  # Token expires in 1 hour
    download_token = DownloadToken(token=token, filename=converter.output_file, expires_at=expires_at)
    db.session.add(download_token)
    db.session.commit()
    return token

def remove_uploaded_file(filepath):
    if os.path.exists(filepath):
        os.remove(filepath)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/download_page/<token>')
def download_page(token):
    download_token = DownloadToken.query.filter_by(token=token).first()
    if download_token and download_token.expires_at > datetime.now():
        return render_template('download.html', token=download_token.token)
    else:
        flash('The download link has expired or is invalid.', "error")
        return redirect(url_for('home'))

@app.route('/download/<token>')
def download(token):
    download_token = DownloadToken.query.filter_by(token=token).first()
    if download_token and download_token.expires_at > datetime.now():
        file_path = os.path.join(app.config['OUTPUT_FILES_DEST'], download_token.filename)
        return send_file(file_path, as_attachment=True)
    else:
        flash('The download link has expired or is invalid.', "error")
        return redirect(url_for('home'))

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST' and 'file' in request.files:
        file = request.files['file']
        try:
            filename = files.save(file)
        except UploadNotAllowed:
            flash('File type not allowed.', "error")
            return redirect(url_for('upload'))
        
        filetype = file.content_type
        filepath = os.path.join("uploads", filename)
        output_format = request.form['file-format']

        converter = Converter(filename, filetype, output_format)
        if converter.convert():
            remove_uploaded_file(filepath)
            create_media(converter.output_file_name, filetype, converter.output_file)
            token = create_token(converter)
            return redirect(url_for('download_page', token=token))
        else:
            flash('An error occurred during the conversion. Please try again.', "error")
            return redirect(url_for('upload'))
    return render_template('upload.html')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)