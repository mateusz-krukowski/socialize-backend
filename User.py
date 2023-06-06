from db import db


class User(db.Model):

    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    username = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    description = db.Column(db.String(255))
    profile_picture = db.Column(db.String(255))

    def __init__(self, email, username, password, is_admin=False, description=None, profile_picture=None):
        self.email = email
        self.username = username
        self.password = password
        self.is_admin = is_admin
        self.description = description
        self.profile_picture = profile_picture
