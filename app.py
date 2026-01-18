import os
import uuid
from datetime import datetime, timedelta
from flask import Flask, render_template, redirect, url_for, flash, request, send_from_directory, abort
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename
from config import Config
from models import db, User, FileEntry

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

with app.app_context():
    db.create_all()

@app.route('/', methods=['GET', 'POST'])
def index():
    if current_user.is_authenticated:
        if request.method == 'POST':
            if 'file' not in request.files:
                return redirect(request.url)
            
            file = request.files['file']
            if file.filename == '':
                return redirect(request.url)

            if file:
                filename = secure_filename(file.filename)
                unique_name = str(uuid.uuid4()) + "_" + filename
                save_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_name)
                
                try:
                    file.save(save_path)
                except:
                    return redirect(request.url)

                exp_input = request.form.get('expiration')
                if exp_input == '5_sec':
                    seconds = 5
                elif exp_input == '10_sec':
                    seconds = 10
                else:
                    seconds = int(exp_input) * 3600
                
                link_id = str(uuid.uuid4())[:8]

                new_file = FileEntry(
                    filename=unique_name,
                    original_name=filename,
                    expiration_date=None, 
                    duration_seconds=seconds,
                    unique_link=link_id,
                    author=current_user
                )
                db.session.add(new_file)
                db.session.commit()
                return redirect(url_for('index'))

        user_files = FileEntry.query.filter_by(user_id=current_user.id).order_by(FileEntry.upload_date.desc()).all()
        return render_template('index.html', files=user_files, now_utc=datetime.utcnow())
    
    return render_template('index.html', now_utc=datetime.utcnow())

@app.route('/start_timer/<int:file_id>')
@login_required
def start_timer(file_id):
    file = FileEntry.query.get_or_404(file_id)
    if file.author != current_user:
        return redirect(url_for('index'))
    
    if file.expiration_date is None:
        file.expiration_date = datetime.utcnow() + timedelta(seconds=file.duration_seconds)
        db.session.commit()
    
    return redirect(url_for('index'))

@app.route('/f/<unique_link>')
def download_file(unique_link):
    file_entry = FileEntry.query.filter_by(unique_link=unique_link).first_or_404()

    if file_entry.expiration_date and datetime.utcnow() > file_entry.expiration_date:
        try:
            os.remove(os.path.join(app.config['UPLOAD_FOLDER'], file_entry.filename))
        except:
            pass
        db.session.delete(file_entry)
        db.session.commit()
        return abort(404)

    return send_from_directory(app.config['UPLOAD_FOLDER'], file_entry.filename, as_attachment=True, download_name=file_entry.original_name)

@app.errorhandler(404)
def not_found_error(error):
    return render_template('error.html', title="Файл не найден", message="Срок хранения истек или ссылка неверна."), 404

@app.errorhandler(413)
def too_large_error(error):
    return render_template('error.html', title="Файл слишком большой", message="Максимум 50 МБ."), 413

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated: return redirect(url_for('index'))
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if User.query.filter_by(username=username).first():
            return redirect(url_for('register'))
        user = User(username=username)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated: return redirect(url_for('index'))
    if request.method == 'POST':
        user = User.query.filter_by(username=request.form['username']).first()
        if user and user.check_password(request.form['password']):
            login_user(user)
            return redirect(url_for('index'))
    return render_template('login.html')

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)