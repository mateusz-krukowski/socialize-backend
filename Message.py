from User import User
from db import db


class Message(db.Model):
    __tablename__ = 'messages'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    text = db.Column(db.String(255))
    date = db.Column(db.DateTime)

    user = db.relationship('User', foreign_keys=[user_id])
