from flask import Flask, render_template, request, redirect, url_for, flash, send_file
from flask_uploads import UploadSet, UploadNotAllowed, configure_uploads
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta
from uuid import uuid4
from db import db
from converter import Converter
from models import Media, DownloadToken
from logs import log
from exception import ConvertError
from web import WebDownloader
import os

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

def start_scheduler():
    scheduler = BackgroundScheduler()
    if not scheduler.running:
        scheduler.add_job(func=auto_remove_output_file, trigger="interval", minutes=5)
        scheduler.start()

def create_media(filename, filetype, filepath):
    log(f'Creating media: {filename}', "INFO")
    media = Media(filename=filename, filetype=filetype, filepath=filepath)
    db.session.add(media)
    db.session.commit()

def create_token(output_file) -> str:
    token = str(uuid4())
    expires_at = datetime.now() + timedelta(hours=1)  # Token expires in 1 hour
    download_token = DownloadToken(token=token, filename=output_file, expires_at=expires_at)
    db.session.add(download_token)
    db.session.commit()
    return token

def remove_uploaded_file(filepath):
    if os.path.exists(filepath):
        os.remove(filepath)

def auto_remove_output_file():
    # Run twice when debug mode is on
    with app.app_context():
        expired_tokens = DownloadToken.query.filter(DownloadToken.expires_at < datetime.now()).all()
        for token in expired_tokens:
            file_path = os.path.join(app.config['OUTPUT_FILES_DEST'], token.filename)
            if os.path.exists(file_path):
                os.remove(file_path)
            db.session.delete(token)
        log(f"Removed {len(expired_tokens)} expired files.", "INFO")        
        db.session.commit()

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

@app.route('/convert', methods=['GET', 'POST'])
def convert():
    if request.method == 'POST' and 'file' in request.files:
        print(request.files, request.form, "HERE")
        file = request.files['file']
        try:
            filename = files.save(file)
        except UploadNotAllowed:
            flash('File type not allowed.', "error")
            return redirect(url_for('convert'))
        
        filetype = file.content_type
        output_format = request.form['file-format']

        converter = Converter(filename, filetype, output_format)
        try:
            if converter.convert():
                create_media(converter.output_file_name, filetype, converter.output_file)
                token = create_token(converter.output_file)
                return redirect(url_for('download_page', token=token))
            else:
                raise ConvertError
        except ConvertError:
            flash('An error occurred during the conversion. Please try again.', "error")
            return redirect(url_for('convert'))
        finally: 
            remove_uploaded_file(converter.input_file)
            
    return render_template('convert.html')

@app.route('/web', methods=['GET', 'POST'])
def web():
    log(f'Getting form {request.form}', "DEBUG")
    if request.method == 'POST' and 'url' in request.form:
        url = request.form['url']
        filetype = request.form['file-format']

        web = WebDownloader(url, filetype)
        
        if web.setup_download():
            filename = web.filename
            filepath = os.path.join(os.path.dirname(__file__), "output", filename)
            create_media(filename, filetype, filepath)
            token = create_token(filepath)
            return redirect(url_for('download_page', token=token))    
        else:
            flash('An error occurred during the download. Please try again.', "error")
            return redirect(url_for('web'))
    return render_template('web.html')

@app.route('/test')
def test():
    return render_template('test.html')

def main():
    with app.app_context():
        db.create_all()
    start_scheduler()
    app.run(debug=True)

if __name__ == '__main__':
    main()