from db import db

class DownloadToken(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    token = db.Column(db.String(36), unique=True, nullable=False)
    filename = db.Column(db.String(200), db.ForeignKey('media.filename'), nullable=False)
    expires_at = db.Column(db.DateTime, nullable=False)

    media = db.relationship('Media', backref=db.backref('download_tokens', lazy=True))

    def __repr__(self):
        return f'<DownloadToken {self.token}>'

class Media(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(200), unique=True, nullable=False)
    filetype = db.Column(db.String(50), nullable=False)
    filepath = db.Column(db.String(200), nullable=False)
    filesize = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f'<Media {self.filename}>'