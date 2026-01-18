import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'super-secret-key-change-me'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(BASE_DIR, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Папка для сохранения файлов
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
    # Максимальный размер файла (например, 16 МБ)
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024