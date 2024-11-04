from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_uploads import UploadSet, configure_uploads
from converter import Converter

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
app.config['UPLOADED_FILES_DEST'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 250 * 1024 * 1024
db = SQLAlchemy(app)

AUDIO = ('mp3', 'aac', 'ac3', 'flac', 'wav', 'ogg', 'wma', 'alac', 'aiff', 'amr', 'dts', 'eac3', 'm4a', 'mp2', 'opus', 'pcm', 'vorbis')
VIDEO = ('mp4', 'avi', 'mkv', 'mov', 'flv', 'wmv', 'mpeg', 'webm', '3gp', 'asf', 'm4v', 'ts', 'm2ts', 'vob', 'rm', 'swf')
IMAGE = ('jpeg', 'jpg', 'png', 'bmp', 'gif', 'tiff', 'webp', 'pgm', 'ppm', 'pam', 'pnm', 'tga')
VECTOR = ('svg', 'eps', 'pdf', 'ai', 'emf', 'wmf')
SUBTITLE = ('srt', 'ass', 'ssa', 'sub', 'vtt', 'stl', 'dfxp', 'sami', 'mpl2', 'pjs', 'jacosub')
ARCHIVE = ('tar', 'zip', 'gz', 'bz2', 'rar', '7z')

ALLOWED_EXTENSIONS = AUDIO + VIDEO + IMAGE + SUBTITLE + ARCHIVE

files = UploadSet('files', ALLOWED_EXTENSIONS)
configure_uploads(app, files)

class Media(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(200), nullable=False)
    filetype = db.Column(db.String(50), nullable=False)
    filepath = db.Column(db.String(200), nullable=False)

    def __repr__(self):
        return f'<Media {self.filename}>'

def create_media(filename, filetype, filepath):
    media = Media(filename=filename, filetype=filetype, filepath=filepath)
    db.session.add(media)
    db.session.commit()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST' and 'file' in request.files:
        file = request.files['file']
        filename = files.save(file)
        filetype = file.content_type
        filepath = f'uploads/{filename}'
        output_format = request.form['file-format']
        print(output_format, "output_format")
        Converter(filename, filetype, output_format).convert()

        create_media(filename, filetype, filepath)
        return redirect(url_for('home'))
    return render_template('upload.html')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)