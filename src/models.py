from utils import db

class DownloadToken(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    token = db.Column(db.String(36), unique=True, nullable=False)
    filename = db.Column(db.String(200), nullable=False)
    expires_at = db.Column(db.DateTime, nullable=False)

    def __repr__(self):
        return f'<DownloadToken {self.token}>'

class Media(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(200), nullable=False)
    filetype = db.Column(db.String(50), nullable=False)
    filepath = db.Column(db.String(200), nullable=False)

    def __repr__(self):
        return f'<Media {self.filename}>'