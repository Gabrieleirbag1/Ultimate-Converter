from flask import Flask, render_template, request, redirect, url_for, flash, send_file
from flask_uploads import UploadSet, UploadNotAllowed, configure_uploads
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta
from uuid import uuid4
from db import db
import os

from converter import ManageConversion
from models import Media, DownloadToken
from logs import log
from exception import ConvertError
from web import WebDownloader


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
app.config['UPLOADED_FILES_DEST'] = os.path.join(app.root_path, 'uploads')
app.config['OUTPUT_FILES_DEST'] = os.path.join(app.root_path, 'output')
app.config['MAX_CONTENT_LENGTH'] = 250 * 1024 * 1024
app.secret_key = 'supersecretkey'

db.init_app(app)

AUDIO = ('mp3', 'aac', 'ac3', 'flac', 'wav', 'ogg', 'wma', 'aiff', 'dts', 'eac3', 'm4a', 'mp2', 'opus', 'pcm')
VIDEO = ('mp4', 'avi', 'mkv', 'mov', 'flv', 'wmv', 'mpeg', 'webm', '3gp', 'asf', 'm4v', 'ts', 'm2ts', 'vob', 'rm', 'swf')
IMAGE = ('jpeg', 'jpg', 'png', 'bmp', 'gif', 'tiff', 'webp', 'pgm', 'ppm', 'pam', 'tga', 'eps')
VECTOR = {'svg': 0, 'pdf': 0, 'fig': 2, 'ai': 0, 'sk': 0, 'p2e': 0, 'mif': 256, 'er': 0, 'eps': 0, 'emf': 0, 'dxf': 0, 'drd2': 0, 'cgm': 0}
ARCHIVE = ('7z', 'cb7', 'cbt', 'cbz', 'cpio', 'iso', 'jar', 'tar', 'tar.bz2', 'tar.gz', 'tar.lzma', 'tar.xz', 'tbz2', 'tgz', 'txz', 'zip')

FORMATS = {'audio': AUDIO, 'video': VIDEO, 'image': IMAGE, 'vector': VECTOR, 'archive': ARCHIVE}

ALLOWED_EXTENSIONS = AUDIO + VIDEO + IMAGE + tuple(VECTOR.keys()) + ARCHIVE 

files = UploadSet('files', ALLOWED_EXTENSIONS)
configure_uploads(app, files)

def get_format_category(extension):
    for category, extensions in FORMATS.items():
        if extension in extensions:
            return category
    return None

def start_scheduler():
    scheduler = BackgroundScheduler()
    if not scheduler.running:
        scheduler.add_job(func=auto_remove_output_file, trigger="interval", minutes=5)
        scheduler.start()

def create_media(filename, filetype, filepath):
    log(f'Creating media: {filename}', "INFO")
    media = Media(filename=filename, filetype=filetype, filepath=filepath, filesize=os.path.getsize(filepath))
    db.session.add(media)
    db.session.commit()

def create_token(output_file) -> str:
    token = str(uuid4())
    expires_at = datetime.now() + timedelta(hours=1)  # Token expires in 1 hour
    media = Media.query.filter_by(filepath=output_file).first()
    download_token = DownloadToken(token=token, filename=media.filename, expires_at=expires_at)
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
                try:
                    os.remove(file_path)
                except IsADirectoryError:
                    log(f"Error removing file: {file_path}", "ERROR")
            media = Media.query.filter_by(filename=token.filename).first()
            if media:
                db.session.delete(media)
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
        media = Media.query.filter_by(filename=download_token.filename).first()
        if media:
            file_size_mb = round(media.filesize / (1024 * 1024), 2)
            format = get_format_category(media.filetype)

            log(f" format: {format}", "DEBUG")
            return render_template('download.html', token=download_token.token, filename=media.filename, filesize=file_size_mb, filetype=media.filetype, format=format)
    flash('The download link has expired or is invalid.', "error")
    return redirect(url_for('home'))

@app.route('/download/<token>')
def download(token):
    download_token = DownloadToken.query.filter_by(token=token).first()
    if download_token and download_token.expires_at > datetime.now():
        media = Media.query.filter_by(filename=download_token.filename).first()
        if media:
            return send_file(media.filepath, as_attachment=True)
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
        log(filetype, "DEBUG")
        log(output_format, "DEBUG")

        conversion = ManageConversion(filename, output_format, filetype)
        try:
            if conversion.converter.convert():
                create_media(conversion.converter.output_file_name, os.path.basename(output_format), conversion.converter.output_file)
                token = create_token(conversion.converter.output_file)
                return redirect(url_for('download_page', token=token))
            else:
                raise ConvertError
        except ConvertError:
            flash('An error occurred during the conversion. Please try again.', "error")
            return redirect(url_for('convert'))
        finally: 
            remove_uploaded_file(conversion.converter.input_file)
    return render_template('convert.html')

@app.route('/web', methods=['GET', 'POST'])
def web():
    log(f'Getting form {request.form}', "DEBUG")
    if request.method == 'POST' and 'url' in request.form:
        url = request.form['url']
        filetype = request.form['file-format']
        log(f"File format web {filetype}", "DEBUG")
        web = WebDownloader(url, filetype)
        
        if web.setup_download():
            filename = os.path.basename(web.filename)
            filepath = web.filename
            filetype = os.path.basename(filetype)
            if os.path.exists(filepath):
                create_media(filename, filetype, filepath)
                token = create_token(filepath)
            else:
                flash('An error occurred during the conversion', "error")
                return redirect(url_for('web'))
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