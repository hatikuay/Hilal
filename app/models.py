# File: app/models.py
from . import db
from flask_login import UserMixin
from sqlalchemy import Text


class Role:
    GUEST = "guest"
    USER = "user"
    ADMIN = "admin"
    EDITOR = "editor"

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id       = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(Text, nullable=False)
    role     = db.Column(db.String(50), default=Role.USER)

    notes    = db.relationship('Note', backref='owner', lazy=True)


class Note(db.Model):
    __tablename__ = 'notes'
    id       = db.Column(db.Integer, primary_key=True)
    title    = db.Column(db.String(100))
    content  = db.Column(db.Text)
    user_id  = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
