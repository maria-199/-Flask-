from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory, make_response
import os
import uuid
from werkzeug.utils import secure_filename



app = Flask(__name__)
app.secret_key = 'cggcgcgcjcgc'  # секретный ключ

UPLOAD_ROOT = 'uploads'
ALLOWED_EXTENSIONS = {'txt','pdf', 'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_user_id():
    user_id = request.cookies.get('user_id')
    if not user_id:
        user_id = str(uuid.uuid4())
    return user_id

@app.route('/', methods=['GET'])
def index():
    user_id = get_user_id()
    user_folder = os.path.join(UPLOAD_ROOT, user_id)
    if not os.path.exists(user_folder):
        os.makedirs(user_folder)
    files = os.listdir(user_folder)
    response = make_response(render_template('user_files.html', files=files))
    # Устанавливаем cookie при первом посещении
    if not request.cookies.get('user_id'):
        response.set_cookie('user_id', user_id)
    return response

@app.route('/upload', methods=['POST'])
def upload():
    user_id = get_user_id()
    file = request.files.get('file')
    if not file or file.filename == '':
        flash('Файл не выбран.')
        return redirect(url_for('index'))
    if allowed_file(file.filename):
        filename = secure_filename(file.filename)
        user_folder = os.path.join(UPLOAD_ROOT, user_id)
        os.makedirs(user_folder, exist_ok=True)
        filepath = os.path.join(user_folder, filename)
        file.save(filepath)
        flash(f'Файл "{filename}" успешно загружен.')
    else:
        flash('Недопустимый тип файла.')
    return redirect(url_for('index'))

@app.route('/download/<filename>')
def download(filename):
    user_id = get_user_id()
    user_folder = os.path.join(UPLOAD_ROOT, user_id)
    return send_from_directory(user_folder, filename)

if __name__ == '__main__':
    os.makedirs(UPLOAD_ROOT, exist_ok=True)
    app.run(debug=True)