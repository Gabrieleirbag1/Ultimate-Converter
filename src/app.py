from flask import Flask, render_template, request, redirect, url_for, flash, send_file
from flask_uploads import UploadSet, UploadNotAllowed, configure_uploads, ALL
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta
from uuid import uuid4
from db import db
import os

from utils import ALLOWED_EXTENSIONS, FORMATS
from converter import ManageConversion
from models import Media, DownloadToken
from logs import log
from exception import ConvertError
from web import WebDownloader

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
app.config['UPLOADED_FILES_DEST'] = os.path.join(app.root_path, 'uploads')
app.config['OUTPUT_FILES_DEST'] = os.path.join(app.root_path, 'output')
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024 # 1000 MB
app.config['MAX_OUTPUT_FOLDER_SIZE'] = 20 * 1024 * 1024 * 1024  # 20 GB
app.secret_key = os.urandom(24) 

db.init_app(app)

files = UploadSet('files', ALL)
configure_uploads(app, files)

def get_format_category(extension):
    for category, extensions in FORMATS.items():
        if extension in extensions:
            return category
    return None

def get_full_extension(filename):
    for ext in ALLOWED_EXTENSIONS:
        if filename.lower().endswith(ext):
            return ext
    return None

def get_folder_size(folder: str) -> int:
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(folder):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            total_size += os.path.getsize(fp)
    return total_size

def check_size(file_size: int) -> bool:
    output_folder_size = get_folder_size(app.config['OUTPUT_FILES_DEST'])
    max_size = app.config['MAX_OUTPUT_FOLDER_SIZE']
    if output_folder_size + file_size > max_size:
        return False
    return True

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

@app.route('/download_page/<token>/')
def download_page(token):
    download_token = DownloadToken.query.filter_by(token=token).first()
    if download_token and download_token.expires_at > datetime.now():
        media = Media.query.filter_by(filename=download_token.filename).first()
        if media:
            file_size_mb = round(media.filesize / (1024 * 1024), 2)
            format = get_format_category(media.filetype.split(' (autotrace)')[0])
            log(f" format: {format}, {media.filetype}, {media.filetype.split(' (autotrace)')[0]}", "DEBUG")
            return render_template('download.html', token=download_token.token, filename=media.filename, filesize=file_size_mb, filetype=media.filetype, format=format)
    flash('The download link has expired or is invalid.', "error")
    return redirect(url_for('home'))

@app.route('/download/<token>/')
def download(token):
    download_token = DownloadToken.query.filter_by(token=token).first()
    if download_token and download_token.expires_at > datetime.now():
        media = Media.query.filter_by(filename=download_token.filename).first()
        if media:
            return send_file(media.filepath, as_attachment=True)
    flash('The download link has expired or is invalid.', "error")
    return redirect(url_for('home'))

@app.route('/convert/', methods=['GET', 'POST'])
def convert():
    if request.method == 'POST' and 'file' in request.files:
        file = request.files['file']
        file_size = len(file.read())
        file.seek(0)  # Reset file pointer to the beginning

        if not check_size(file_size):
            flash('The total size of the output folder exceeds the maximum allowed size.', "error")
            return redirect(url_for('convert'))

        filetype = get_full_extension(file.filename)
        output_format = request.form['file-format']
        try:
            if filetype in ALLOWED_EXTENSIONS:
                filename = files.save(file)
            else:
                raise UploadNotAllowed
        except UploadNotAllowed:
            flash('File type not allowed.', "error")
            return redirect(url_for('convert'))
        
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

@app.route('/web/', methods=['GET', 'POST'])
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
            file_size = os.path.getsize(filepath)
            
            if not check_size(file_size):
                flash('The total size of the output folder exceeds the maximum allowed size.', "error")
                os.remove(filepath)  # Remove the downloaded file
                return redirect(url_for('web'))

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

def main():
    with app.app_context():
        db.create_all()
    start_scheduler()

if __name__ == '__main__':
    main()
    app.run(port=8081, debug=True)