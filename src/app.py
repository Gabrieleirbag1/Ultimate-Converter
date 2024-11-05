from flask import render_template, request, redirect, url_for, flash, send_file, get_flashed_messages
from flask_uploads import UploadSet, UploadNotAllowed, configure_uploads
from converter import Converter
from models import Media, DownloadToken
from datetime import datetime, timedelta
from utils import app, db, ALLOWED_EXTENSIONS
import uuid, os

files = UploadSet('files', ALLOWED_EXTENSIONS)
configure_uploads(app, files)

def create_media(filename, filetype, filepath):
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

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/download_page/<token>')
def download_page(token):
    download_token = DownloadToken.query.filter_by(token=token).first()
    if download_token and download_token.expires_at > datetime.now():
        return render_template('download.html', filename=download_token.filename)
    else:
        flash('The download link has expired or is invalid.')
        return redirect(url_for('home'))
    
@app.route('/download/<filename>')
def download(filename):
    print("Download: ", filename)
    return send_file(filename, as_attachment=True)

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST' and 'file' in request.files:
        get_flashed_messages()
        file = request.files['file']
        try:
            filename = files.save(file)
        except UploadNotAllowed:
            flash('File type not allowed.')
            return redirect(url_for('upload'))
        
        filetype = file.content_type
        filepath = os.path.join("uploads", filename)
        output_format = request.form['file-format']

        converter = Converter(filename, filetype, output_format)
        if converter.convert():
            create_media(converter.output_file, filetype, filepath)
            token = create_token(converter)
            return redirect(url_for('download_page', token=token))
        else:
            flash('An error occurred during the conversion. Please try again.')
            return redirect(url_for('upload'))
    return render_template('upload.html')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)