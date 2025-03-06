from flask import Flask, render_template, request, redirect, url_for, flash, send_file, Response
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
app.config['MAX_CONTENT_LENGTH'] = 1 * 1024 * 1024 * 1024  # 1GB
app.config['MAX_OUTPUT_FOLDER_SIZE'] = 20 * 1024 * 1024 * 1024  # 20 GB
app.secret_key = os.urandom(24) 

db.init_app(app)

files = UploadSet('files', ALL)
configure_uploads(app, files)

def get_format_category(extension: str) -> str | None:
    """This function returns the category of the format based on the extension.
    
    :param str extension: The extension of the file.
    
    :return: The category of the format.
    :rtype: str | None"""
    for category, extensions in FORMATS.items():
        if extension in extensions:
            return category
    return None

def get_full_extension(filename: str) -> str | None:
    """This function returns the full extension of the file.
    
    :param str filename: The name of the file.
    
    :return: The full extension of the file.
    :rtype: str | None"""
    for ext in ALLOWED_EXTENSIONS:
        if filename.lower().endswith(ext):
            return ext
    return None

def get_folder_size(folder: str) -> int:
    """This function returns the total size of the folder.
    
    :param str folder: The path to the folder.
    
    :return: The total size of the folder.
    :rtype: int"""
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(folder):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            total_size += os.path.getsize(fp)
    return total_size

def check_size(file_size: int) -> bool:
    """This function checks if the total size of the output folder exceeds the maximum allowed size.
    
    :param int file_size: The size of the file to be added to the output folder.
    
    :return: True if the total size of the output folder does not exceed the maximum allowed size, False otherwise.
    :rtype: bool"""
    output_folder_size = get_folder_size(app.config['OUTPUT_FILES_DEST'])
    max_size = app.config['MAX_OUTPUT_FOLDER_SIZE']
    if output_folder_size + file_size > max_size:
        return False
    return True

def start_scheduler():
    """This function starts the scheduler to remove expired files."""
    scheduler = BackgroundScheduler()
    if not scheduler.running:
        scheduler.add_job(func=auto_remove_output_file, trigger="interval", minutes=5)
        scheduler.start()

def create_media(filename: str, filetype: str, filepath: str):
    """This function creates a new media entry in the database.
    
    :param str filename: The name of the file.
    :param str filetype: The type of the file.
    :param str filepath: The path to the file."""
    log(f'Creating media: {filename}', "INFO")
    existing_media = Media.query.filter_by(filename=filename).first()
    if existing_media:
        log(f'Media with filename {filename} already exists. Updating existing entry.', "INFO")
        existing_media.filetype = filetype
        existing_media.filepath = filepath
        existing_media.filesize = os.path.getsize(filepath)
    else:
        media = Media(filename=filename, filetype=filetype, filepath=filepath, filesize=os.path.getsize(filepath))
        db.session.add(media)
    db.session.commit()

def create_token(output_file: str) -> str:
    """This function creates a download token for the output file.
    
    :param str output_file: The path to the output file.
    
    :return: The download token.
    :rtype: str"""
    token = str(uuid4())
    expires_at = datetime.now() + timedelta(hours=1)  # Token expires in 1 hour
    media = Media.query.filter_by(filepath=output_file).first()
    download_token = DownloadToken(token=token, filename=media.filename, expires_at=expires_at)
    db.session.add(download_token)
    db.session.commit()
    return token

def remove_uploaded_file(filepath: str):
    """This function removes the uploaded file.

    :param str filepath: The path to the uploaded file."""
    if os.path.exists(filepath):
        os.remove(filepath)

def auto_remove_output_file():
    """This function removes expired files from the output folder."""
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
def home() -> Response:
    """This function renders the home page.
    
    :return: The home page.
    :rtype: Response"""
    return render_template('index.html')

@app.route('/download_page/<token>/')
def download_page(token: str) -> Response:
    """This function renders the download page.
    
    :param str token: The download token.
    
    :return: The download page.
    :rtype: Response
    """
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
def download(token: str) -> Response:
    """This function downloads the file.
    
    :param str token: The download token.
    
    :return: The file to download.
    :rtype: Response"""
    download_token = DownloadToken.query.filter_by(token=token).first()
    if download_token and download_token.expires_at > datetime.now():
        media = Media.query.filter_by(filename=download_token.filename).first()
        if media:
            return send_file(media.filepath, as_attachment=True)
    flash('The download link has expired or is invalid.', "error")
    return redirect(url_for('home'))

@app.route('/convert/', methods=['GET', 'POST'])
def convert() -> Response:
    """This function converts the uploaded file to the desired format.
    
    :return: The convert page or the download page.
    :rtype: Response
    
    :raises UploadNotAllowed: If the file type is not allowed.
    :raises ConvertError: If an error occurs during the conversion."""
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
def web() -> Response:
    """This function downloads the file from the web.
    
    :return: The web page or the download page.
    :rtype: Response"""
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
    """This function initializes the database and starts the scheduler."""
    with app.app_context():
        db.create_all()
    start_scheduler()

if __name__ == '__main__':
    main()
    app.run(port=8082, debug=True)