from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    files = db.relationship('FileEntry', backref='author', lazy=True)

class FileEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(300), nullable=False)  # Имя файла на диске (безопасное)
    original_name = db.Column(db.String(300), nullable=False) # Реальное имя
    upload_date = db.Column(db.DateTime, default=datetime.utcnow)
    expiration_date = db.Column(db.DateTime, nullable=False) # Когда удалять
    unique_link = db.Column(db.String(100), unique=True, nullable=False) # Ссылка для скачивания
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)