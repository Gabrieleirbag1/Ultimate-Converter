from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_uploads import UploadSet, configure_uploads, IMAGES, AUDIO, DATA
from werkzeug.utils import secure_filename
from werkzeug.datastructures import  FileStorage
from converter import Converter

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
app.config['UPLOADED_FILES_DEST'] = 'uploads'
db = SQLAlchemy(app)

files = UploadSet('files', IMAGES + AUDIO + DATA)
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
        Converter(filename, filetype, 'png').convert()

        create_media(filename, filetype, filepath)
        return redirect(url_for('home'))
    return render_template('upload.html')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)