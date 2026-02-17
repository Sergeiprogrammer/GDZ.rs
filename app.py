from flask import Flask, render_template, request, jsonify, redirect, url_for, session, render_template_string
from datetime import datetime
import os
import platform
from dbapi import DB
from tgbot import Telegramm_sent
from werkzeug.utils import secure_filename
from email_module import Email
import random

app = Flask(__name__)

app.secret_key = 'your_secret_key'  # Задайте секретный ключ для сессий (замените на безопасный ключ в продакшене) !не используеться сайтом!
app.config['UPLOAD_FOLDER'] = '/home/sergeyeofjhgu/gdz.rs/uploads'
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024  # 5 МБ

FILES_LIMIT = 10
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'pdf', 'pptx', 'doc', 'docx'}
data = {}
forum_data = {}
verification_codes = {}

# Определение операционной системы для установки базового каталога
if platform.system() == 'Windows':
    base_dir = "D:\\windos_custom\\gdz.rs"
    db_path = os.path.join(base_dir, 'main.db')
    db_forum_path = os.path.join(base_dir, 'forum.db')
    db_predmet_path = os.path.join(base_dir, 'predmet.db')
    db_system_path = os.path.join(base_dir, 'system.db')
else:
    base_dir = os.path.join("/", 'home', 'sergeyeofjhgu', 'gdz.rs')
    db_path = os.path.join(base_dir, 'main.db')
    db_system_path = os.path.join(base_dir, 'system.db')
    db_forum_path = os.path.join(base_dir, 'forum.db')
    db_predmet_path = os.path.join(base_dir, 'predmet.db')
sigma = []

@app.before_request
def check_ban_status():
    username = session.get('user')  # Получаем текущего пользователя из сессии

    # Проверка блокировки пользователя по имени
    db = DB(db_path)
    ban_or_not = db.check_user_ban(username)
    if ban_or_not:
        session.pop('user', None)  # Удаляем пользователя из сессии
        return "Ваш налог блокирован.", 403

# Главная страница
# оптимизированно
@app.route('/')
def home():
    if 'user' in session:  # Проверяем, есть ли пользователь в сессии
        #username = session['user']
        # пока не используеться
        #db = DB(db_path)
        #money = db.give_money(username)
        #money = 0
        return render_template("index.html")
    else:
        return render_template("index.html" , is_register="направите налог")

# Страница "помщь за завршни"
#оптимизированно
@app.route('/pomoc_za_zavrsni', methods=['GET', 'POST'])
def pomoc_za_zavrsni():
    if request.method == 'POST':
        selected_language = request.form.get('language')
        if selected_language == 'serbian':
            return render_template("zavrsni.html")
        elif selected_language == 'russian':
            return render_template("zavrsni_ru.html")
        elif selected_language == 'english':
            return render_template("zavrsni_en.html")
    # Если метод GET, показываем страницу с выбором языка
    return '''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Изаберите језик</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                text-align: center;
                margin-top: 50px;
                background-color: #f9f9f9;
                color: #333;
            }
            button {
                font-size: 16px;
                padding: 10px 20px;
                margin: 10px;
                border: none;
                border-radius: 5px;
                cursor: pointer;
                background-color: #2c3e50;
                color: white;
                transition: background-color 0.3s ease;
            }
            button:hover {
                background-color: #34495e;
            }
        </style>
    </head>
    <body>
        <h1>Изаберите језик</h1>
        <form method="POST">
            <button type="submit" name="language" value="serbian">Српски</button>
            <button type="submit" name="language" value="russian">Русский</button>
            <button type="submit" name="language" value="english">English</button>
        </form>
    </body>
    </html>
    '''

# Выбор класса для предмета
# оптимизированно
@app.route('/predmet/<ime>', methods=['GET', 'POST'])
def class1(ime):  # Теперь функция принимает `ime`
    if request.method == 'POST':
        ime = request.form.get('ime')  # Данные из формы
        razred = request.form.get('razred')

        if not ime or not razred:
            return "Ошибка: отсутствуют данные", 400
        db = DB(db_predmet_path)
        link = db.get_link_to_info(razred, ime)

        if not link:
            return "Ошибка: ссылка не найдена", 404
        return redirect(link)
    return render_template("select class.html", ime=ime)


#@app.route('/predmet/<ime>/<int:razred>')
#def show_razred(ime, razred):
    #db = DB(db_predmet_path)
    #link = db.get_link_to_info(razred, ime)
    #return redirect(link)
#_______________________________________________не нужный код

# Отображение домашней работы
#@app.route('/predmet/<ime>/<int:razred>/<ucbenik>/<homework_name>')
#def show_home_work(ime, razred, ucbenik, homework_name):
    #static_dir = os.path.join(base_dir, "static", ime, str(razred), ucbenik, "images", homework_name)
    #relative_path = os.path.relpath(static_dir, base_dir)
    #web_path = Path(relative_path).as_posix() + ".jpg"
    #print(web_path)
    #return render_template("show_home_work.html", image=web_path)

# Отображение списка учебников
#@app.route('/predmet/<ime>/<int:razred>/<ucbenik>')
#def show_home_works(ime, razred, ucbenik):
    #image_info = []
    #static_dir = os.path.join(base_dir, "static", ime, str(razred), ucbenik, "images")
    #relative_path = os.path.relpath(static_dir, base_dir)
    #for paths, directories, files in os.walk(static_dir):
        #for i in files:
            #path = Path(os.path.join(relative_path, i)).as_posix()
            #image_info.append((path, i[:-4]))  # Используем имя файла без расширения
    #return render_template("all_home_works.html", image_info=image_info, ime=ime, razred=razred, ucbenik=ucbenik)

# Выбор учебника для класса
#@app.route('/predmet/<ime>/<int:razred>')
#def show_razred(ime, razred):
    #info = []
    #information = []
    #url = []
    #icons = []
    #static_dir = os.path.join(base_dir, "static", ime, str(razred))
    #print(static_dir)

    #for paths, directories, files in os.walk(static_dir):
        #if "images" not in paths:
            #info.append(os.path.basename(paths))
            #relative_path = os.path.relpath(paths, base_dir)
            #web_path = Path(relative_path).as_posix()
            #icons.append(f"{web_path}/Icon.jpg")
            #information.append(os.path.join(paths, "info.txt"))

    #if icons:
        # Удаляем первый элемент, если необходимо (корректируем оба списка)
        #information.pop(0)
        #icons.pop(0)
        #info.pop(0)
    #try:
        #for i in information:
            #with open(i, 'r') as file:
                #content = file.read()
                #url.append(content)
        #information.clear()
    #except:
        #return render_template("all_books.html", ime=ime, razred=razred)
    # Объединяем списки иконок и информации
    #image_info = list(zip(icons, info , url))
    #print(image_info)
    #return render_template("all_books.html", image_info=image_info, ime=ime, razred=razred , url = url)

#____________________________________________________________

# Регистрация
# оптимизированно
@app.route('/register', methods=['GET', 'POST'])
def register():
    global verification_codes  # Делаем словарь глобальным

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user_mail = request.form.get('email', '').strip().lower()  # Убираем пробелы, приводим в lowercase
        verification_code = request.form.get('verification_code')

        db = DB(db_path)  # Создаём экземпляр класса DB

        try:
            stored_code = verification_codes.get(user_mail)  # Теперь email точно совпадёт

            if not stored_code:
                return f"Грешка: код не был отправлен на этот email! Debug: {user_mail}, {verification_codes}", 400

            if verification_code == stored_code:
                result = db.add_user(username, password, user_mail)
                if result is True:
                    session['user'] = username
                    del verification_codes[user_mail]  # Удаляем код после успешной регистрации
                    return redirect(url_for('login'))
                else:
                    return f"Грешка у регестрацији: {result}", 400
            else:
                return f"Грешка: невалидан код потврде! Debug: {verification_code} ≠ {stored_code}", 400
        except Exception as e:
            print(f"Ошибка при регистрации: {e}")
            return "Дошло до грешке у прављању налога", 500


verification_codes = {}  # Должно быть глобально

@app.route("/send_verification_code", methods=["POST"])
def send_verification_code():
    global verification_codes  # Делаем словарь глобальным

    data = request.json
    email = data.get("email", "").strip().lower()  # Убираем пробелы и делаем lowercase

    if not email:
        return jsonify({"status": "error", "message": "E-mail обязателен!"}), 400

    code = str(random.randint(100000, 999999))  # Генерация 6-значного кода
    verification_codes[email] = code  # Сохраняем код в памяти сервера

    email_sender = Email(email)
    email_sender.verify_email(f"Ваш код подтверждения: {code}")

    return jsonify({"status": "success", "message": "Код отправлен на email!"})


# Форум
@app.route('/forum/<int:page>', methods=['GET', 'POST'])
def forum(page):
    return render_template('in_development.html')
    #if 'user' in session:
        #db = DB(db_forum_path)
        #info = db.get_status(page)
        #print(info)
        #return render_template("forum.html" ,forums = info , page=page)
    #else:
        #return redirect(url_for('register'))

#@app.route('/forum/delete/<username>/<message_id>', methods=['GET', 'POST'])
#def delete_1(username,message_id):
    #if session['user'] == username:
        #db = DB(db_forum_path)
        #result = db.delete_message(message_id)
        #if result:
           #return "ураћено успешно"
        #else:
            #return "не може бити ураћено"
    #else:
        #return "то није твоја порука"


#@app.route('/forum/<page_name>/<forum_id>', methods=['GET', 'POST'])
#def view1(page_name,forum_id):
    #if 'user' in session:
        #db = DB(db_path)
        #info1 = [session['user'], forum_id]
        #has_read = db.is_that_readed(info1)
        #if not has_read:
            #db_forum = DB(db_forum_path)
            #db_forum.popularity_add(info1)
            #db.make_it_readed(info1)
        #if request.method == 'POST':
            #comment_text = request.form.get('comment')
            #if comment_text:
                #now = datetime.now()
                #time = f"{now.hour}:{now.minute}:{now.day}:{now.month}:{now.year}"
                #info1 = {
                    #'username': session.get('user'),
                    #'time': time,
                    #'forum_name': page_name,
                    #'message': comment_text
                #}
                #db = DB(db_forum_path)
                #answer = db.add_messages_to_forum(info1)
                #if answer != True:
                    #return "грешка неможе да пошаљи поруку"
                #return redirect(url_for('view1', page_name=page_name , forum_id=forum_id))
        #db = DB(db_forum_path)
        # Загружаем первую страницу (page=0)
        #info = list(db.get_messages(page_name, 0))
        #return render_template('forum_view.html', page_name=page_name, forum_id=forum_id, forums=info)
    #else:
        #return redirect(url_for('register'))

# Новый маршрут для обработки AJAX-запросов
# В файле вашего основного приложения Flask
#@app.route('/forum/<page_name>/ajax', methods=['POST'])
#def ajax_handler(page_name):
    #if 'user' in session:
        #data = request.get_json()
        #page = data.get('page', 0)
        #print(page)
        #db = DB(db_forum_path)
        #special = True
        #messages = db.get_messages(page_name, page ,special)
        #return jsonify({'response_text': messages})
    #else:
        #return redirect(url_for('register'))

#функция входа в аккаунт
# оптимизированно
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        db = DB(db_path)  # Создаем экземпляр класса DB

        result = db.validate(username, password)
        if result == True:
            session['user'] = username
            teacher_rights = db.validate_teacher_rights(username)
            session['teacher'] = teacher_rights # Добавляем пользователя в сессию
            return redirect(url_for('home'))  # Перенаправляем на главную страницу
        else:
            return f"грешка у моменат улоза на налог"

    return render_template('login.html', text="уђи на налог")

# Выход из аккаунта
# оптимизированно
@app.route('/logout')
def logout():
    session.pop('user', None)   # Удаляем пользователя из сессии
    #session.pop('avatar', None) # Удаляем аватар из сессии
    return redirect(url_for('login'))


# загрузка фалов
# оптимизированно
@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    global data

    if 'user' not in session:
        return redirect(url_for('register'))  # Если нет пользователя, отправляем на регистрацию

    username = session.get('user')

    # Инициализация данных пользователя
    if username not in data or data[username][1] != datetime.now().day:
        data[username] = [0, datetime.now().day]

    # Проверка лимита публикаций
    if data[username][0] >= FILES_LIMIT:
        return f"данас ви ста послали {FILES_LIMIT} могуђност да шаљите више биче доступна сутра", 400

    if request.method == 'POST':
        file = request.files.get('fileUpload')  # <-- совпадает с HTML
        text = request.form.get('textInput')  # <-- совпадает с HTML
        task_type = request.form.get('taskType')  # <-- совпадает с HTML

        print("Полученные данные:", request.form)  # Проверяем, что реально пришло

        if not task_type:
            return "ви нисте додали тип задатка", 400

        teacher = session.get('teacher', 'неизвестен')

        # Если есть только текст без файла
        if not file or file.filename == '':
            message = (
                f"Тип задания: {task_type}\n"
                f"Информация: {text}\n"
                f"Статус учителя: {teacher}"
            )
            print(message)
            Telegramm_sent.send_text_to_me(message)  # Отправляем только текст
        else:
            try:
                # Проверяем расширение файла
                if '.' not in file.filename:
                    return "овај фајл није исправан", 400

                file_extension = file.filename.rsplit('.', 1)[1].lower()
                if file_extension not in ALLOWED_EXTENSIONS:
                    return f"овај тип фајла није доступан променити тип фајла кроз неки конвертат на један из ових {ALLOWED_EXTENSIONS} сад ви послали фајл : {file_extension}", 400

                filename = secure_filename(file.filename)
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)

                print(f"Сохраняем файл: {file_path}")  # Отладка

                # оздаём папку, если её нет
                if not os.path.exists(app.config['UPLOAD_FOLDER']):
                    os.makedirs(app.config['UPLOAD_FOLDER'])

                file.save(file_path)

                message = (
                    f"Файл от пользователя {username}:\n"
                    f"Тип задания: {task_type}\n"
                    f"Информация: {text}\n"
                    f"Статус учителя: {teacher}"
                )

                print("Отправка сообщения в Telegram")
                Telegramm_sent.send_text_to_me(message)
                Telegramm_sent.send_file_as_document(file_path, file_name=file.filename)

                try:
                    os.remove(file_path)
                    print(f"Файл {file_path} удалён.")
                except FileNotFoundError:
                    print(f"Файл {file_path} не найден для удаления.")

            except:
                print("грешка при раду са фајлом")
                return "грешка при раду са фајлом", 500  # Показываем ошибку в ответе (для отладки)

        # Обновляем счётчик публикаций
        data[username][0] += 1
        remaining = FILES_LIMIT - data[username][0]
        return render_template_string(f"за данас ви можита да пошаљите јеш {remaining} фајлова")

    return "Метод GET није доступан за ову страну", 405  # Если кто-то пытается сделать GET-запрос

# оптимизированно
@app.route('/submit-homework')
def submit_homework():
    if 'user' in session:
        return render_template('homework_sent.html')
    else:
        return redirect(url_for('register'))

@app.route('/create_forum', methods=['GET', 'POST'])
def create_forum():
    if 'user' not in session:
        return redirect(url_for('register'))  # Перенаправляем неавторизованного пользователя

    username = session['user']  # Получаем имя пользователя

    # Инициализация данных пользователя
    if username not in forum_data:
        forum_data[username] = [0, datetime.now().day]

    # Обнуляем счётчик публикаций, если день изменился
    if forum_data[username][1] != datetime.now().day:
        forum_data[username] = [0, datetime.now().day]

    # Проверяем лимит публикаций
    if forum_data[username][0] >= 2:
        return "ви достигли лимита публикације форума за данас пробајте сутре"

    if request.method == 'POST':
        try:
            # Считываем данные формы
            topic = request.form.get('topic')
            title = request.form.get('title')
            additional_info = request.form.get('additional_info')
            school = request.form.get('school', 'None')  # Если школа не указана, устанавливаем 'None'

            if not topic or not title:  # Проверяем обязательные поля
                return "ви нисте додали тему и назив"

            # Формируем данные для базы
            info = {
                'topic': topic,
                'title': title,
                'additional_info': additional_info,
                'school': school,
                'author_name': username
            }

            # Сохраняем данные в базу
            db = DB(db_forum_path)  # Укажите реальный путь к вашей базе данных
            result = db.create_forum(info)
            if result == "405":
                return "грешка на сајту"

            # Увеличиваем счётчик публикаций
            forum_data[username][0] += 1

            return (f'Тема: {topic}<br>'
                    f'Название: {title}<br>'
                    f'Доп. информация: {additional_info}<br>'
                    f'Школа: {school}')
        except Exception as e:
            print(f"Ошибка: {e}")
            return "грешка на сајту"

    # Если метод GET, отображаем форму
    return render_template('create_forum.html')

@app.route('/admin_panel', methods=['GET', 'POST'])
def admina_panel():
    username = session.get('user')  # Получаем имя пользователя из сессии
    db = DB(db_path)  # Создаем экземпляр класса DB
    result = db.validate_rights(username)  # Проверяем права администратора

    if result:
        if request.method == 'POST':
            try:
                # Получаем данные из формы
                topic = request.form.get('topic')
                title = request.form.get('title')
                additional_info = request.form.get('additional_info')
                # Отправляем информацию в Telegram
                Telegramm_sent.send_admin_submission(topic, title, additional_info, username)

                return (
                    f"Тема: {topic}<br>Заголовок: {title}<br>"
                    f"информација успешно послана после провере она биче додана на сајт"
                )
            except Exception as e:
                print(f"Ошибка: {e}")
                return "грешка на сајту"
        else:
            return render_template('admin_panel.html')
    else:
        return render_template('404.html'), 404

@app.route('/teacher_info')
def teacher_info():
    srednja_skola = "https://drive.google.com/drive/folders/1BvyPIkqwwJnpFxDvLiIcz0HdH2BygeOC?usp=drive_link"
    osnovna_skola = "https://drive.google.com/drive/folders/1csOAQc9l2WKyUQaDUTXq8RiYRoVAnwiE?usp=drive_link"
    return render_template('teacher_info.html', osnovna_skola=osnovna_skola, srednja_skola=srednja_skola)

# оптимизированно
@app.route('/settings', methods=['GET', 'POST'])
def settings():
    try:
        if 'user' in session:
            username = session['user']
            if request.method == 'POST':
                teacher_code = request.form.get('teacher_code')
                if not teacher_code:
                    return render_template('settings.html', username=username, error="ако желиш да добије преференције наставника добије специални код")

                code_db = db_system_path
                usernames_db = db_path

                if not code_db or not usernames_db:
                    return render_template('settings.html', username=username, error="грешка на сајту")

                db = DB(usernames_db)
                result = db.give_teacher_rights(username, teacher_code, code_db, usernames_db)

                if result:
                    return render_template('settings.html', username=username, message=result, category="ви сте добили преференције наставника")
                    session['teacher'] = True # Добавляем пользователя в сессию
                else:
                    return render_template('settings.html', username=username, error="неправилан код наставника")
            return render_template('settings.html', username=username)
        else:
            return redirect(url_for('register'))
    except Exception as e:
        print(f"Ошибка: {e}")
        return "грешка на сајту"

@app.route('/api', methods=['GET'])
def api():
    return jsonify({"message": "test 1 if you see that operation succes"})

@app.route('/faq')
def faq():
    return render_template('faq.html')

@app.route('/converter')
def converter():
    return render_template('converter.html')

@app.errorhandler(404)
def page_not_found(e):
    # Можно вернуть кастомный HTML или шаблон
    return render_template('404.html', text=request.path), 404

@app.errorhandler(413)
def too_large(e):
    return "Ошибка: Размер файла превышает допустимые 10 МБ.", 413

# Запуск приложения
if __name__ == '__main__':
    app.run(debug=True)