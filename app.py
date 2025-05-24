    #необходимые модули: Flask для веб-приложения, SQLAlchemy для ORM, os для работы с файлами и путями.
from flask import Flask, render_template, request, redirect, url_for, send_from_directory, flash
from flask_sqlalchemy import SQLAlchemy
import os

    #Инициализация приложения и настройка базы данных
app = Flask(__name__)
    # секретный ключ для flash
app.secret_key = 'asdfghj'

    # Настройка базы данных
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'files.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    #db — объект ORM.
db = SQLAlchemy(app)


    #реализация условий "Хранение данных" и "ORM-модели".
    #Модель ORM (таблица файлов)
class File(db.Model):
    #таблица File с полями: id, filename, order_number.
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    order_number = db.Column(db.Integer, nullable=False)

    # Используется ORM для хранения информации о файлах.
    def __repr__(self):
        return f"<File {self.filename} ({self.order_number})>"


# Создание таблицы при первом запуске
with app.app_context():
    db.create_all()

#работа с файлами и хранение данных
# Папка для загрузки файлов
# Создается папка uploads, если не существует.
UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ограничение допустимых расширений файлов
ALLOWED_EXTENSIONS = {'png',
                      'jpg',
                      'jpeg',
                      'gif',
                      'txt',
                      'pdf',
                      'docx',
                      }

#Функция проверяет допустимость расширения файла перед загрузкой.
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


#главная страница
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        uploaded_file = request.files.get('file')
        if uploaded_file:
            filename = uploaded_file.filename

            # Проверка расширения файла
            if allowed_file(filename):
                #Сохранение файла в папку
                save_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                uploaded_file.save(save_path)

                # Получаем максимальный порядковый номер и увеличиваем на 1
                max_order = db.session.query(db.func.max(File.order_number)).scalar()
                next_order = (max_order or 0) + 1

                # Записываем в базу данных
                new_file = File(filename=filename, order_number=next_order)
                db.session.add(new_file)
                db.session.commit()
            else:
                flash('Ошибка: неподдерживаемый тип файла.', 'danger')

    # Получаем список файлов по порядку (используя ORM)
    files = File.query.order_by(File.order_number).all()
    # Шаблон
    return render_template('index.html', files=files)


# Маршрут для скачивания файла
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


# Маршрут удаления файла
@app.route('/delete/<filename>', methods=['POST'])
def delete_file(filename):
    # Удаляем файл из файловой системы
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if os.path.exists(file_path):
        os.remove(file_path)

    # Удаляем запись из базы данных
    file_record = File.query.filter_by(filename=filename).first()
    if file_record:
        db.session.delete(file_record)
        db.session.commit()

    return redirect(url_for('index'))

# Запуск приложения
if __name__ == '__main__':
    app.run(debug=True)
