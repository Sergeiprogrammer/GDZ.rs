from flask import Flask, render_template, request, jsonify, redirect, url_for, session, render_template_string
from datetime import datetime
import os
import platform
from pathlib import Path
from dbapi import DB
from tgbot import Telegramm_sent
from crypto_utils import Cryptography
from base64 import b64decode

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Задайте секретный ключ для сессий (замените на безопасный ключ в продакшене)
app.config['UPLOAD_FOLDER'] = 'uploads'
data = {}
forum_data = {}


# Определение операционной системы для установки базового каталога
if platform.system() == 'Windows':
    base_dir = "D:\\windos_custom\\gdz.rs"
    db_path = 'main.db'
    db_forum_path = 'forum.db'
    db_system = 'chat.db'
else:
    base_dir = os.path.join("/", 'home', 'sergeyeofjhgu', 'gdz.rs')
    db_path = os.path.join(base_dir, 'main.db')
    db_forum_path = os.path.join(base_dir, 'forum.db')
    db_system = os.path.join(base_dir, 'chat.db')
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
@app.route('/')
def home():
    if 'user' in session:  # Проверяем, есть ли пользователь в сессии
        username = session['user']
        db = DB(db_path)
        money = db.give_money(username)
        if money != 0:
            return render_template("index.html" , money=f"ви имате {money} coins")
        else:
            return render_template("index.html")
    else:
        return render_template("index.html" , money="направите налог")

# Страница "О нас"
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
@app.route('/predmet/<ime>')
def class1(ime):
    return render_template("select class.html", ime=ime)

#_______________________________________________не нужный код

# Отображение домашней работы
@app.route('/predmet/<ime>/<int:razred>/<ucbenik>/<homework_name>')
def show_home_work(ime, razred, ucbenik, homework_name):
    static_dir = os.path.join(base_dir, "static", ime, str(razred), ucbenik, "images", homework_name)
    relative_path = os.path.relpath(static_dir, base_dir)
    web_path = Path(relative_path).as_posix() + ".jpg"
    print(web_path)
    return render_template("show_home_work.html", image=web_path)

# Отображение списка учебников
@app.route('/predmet/<ime>/<int:razred>/<ucbenik>')
def show_home_works(ime, razred, ucbenik):
    image_info = []
    static_dir = os.path.join(base_dir, "static", ime, str(razred), ucbenik, "images")
    relative_path = os.path.relpath(static_dir, base_dir)
    for paths, directories, files in os.walk(static_dir):
        for i in files:
            path = Path(os.path.join(relative_path, i)).as_posix()
            image_info.append((path, i[:-4]))  # Используем имя файла без расширения
    return render_template("all_home_works.html", image_info=image_info, ime=ime, razred=razred, ucbenik=ucbenik)

#_______________________________________________

# Выбор учебника для класса
@app.route('/predmet/<ime>/<int:razred>')
def show_razred(ime, razred):
    info = []
    information = []
    url = []
    icons = []
    static_dir = os.path.join(base_dir, "static", ime, str(razred))
    print(static_dir)

    for paths, directories, files in os.walk(static_dir):
        if "images" not in paths:
            info.append(os.path.basename(paths))
            relative_path = os.path.relpath(paths, base_dir)
            web_path = Path(relative_path).as_posix()
            icons.append(f"{web_path}/Icon.jpg")
            information.append(os.path.join(paths, "info.txt"))

    if icons:
        # Удаляем первый элемент, если необходимо (корректируем оба списка)
        information.pop(0)
        icons.pop(0)
        info.pop(0)
    try:
        for i in information:
            with open(i, 'r') as file:
                content = file.read()
                url.append(content)
        information.clear()
    except:
        return render_template("all_books.html", ime=ime, razred=razred)
    # Объединяем списки иконок и информации
    image_info = list(zip(icons, info , url))
    print(image_info)
    return render_template("all_books.html", image_info=image_info, ime=ime, razred=razred , url = url)


# Регистрация
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        avatar = request.files.get('image_file')

        db = DB(db_path)  # Создаем экземпляр класса DB

        try:
            result = db.add_user(username, password)  # Убираем fingerprint
            if username and password and result == True:
                session['user'] = username
                # Обработка аватара при необходимости...
                if avatar:
                    avatar.save(f'static/avatars/{username}.png')  # Пример сохранения

                return redirect(url_for('login'))
            else:
                return f"грешка у регестрацији: {result}"
        except Exception as e:
            # Логирование ошибки (можно использовать logging вместо print)
            print(f"Ошибка при регистрации: {e}")
            return "дошло до грешке у правлианју налога"

    # Для GET-запроса возвращаем страницу регистрации
    return render_template('create_account.html', text="Регестрирати")

# Форум
@app.route('/forum/<int:page>', methods=['GET', 'POST'])
def forum(page):
    if 'user' in session:
        db = DB(db_forum_path)
        info = db.get_status(page)
        print(info)
        return render_template("forum.html" ,forums = info , page=page)
    else:
        return redirect(url_for('register'))

@app.route('/forum/delete/<username>/<message_id>', methods=['GET', 'POST'])
def delete_1(username,message_id):
    if session['user'] == username:
        db = DB(db_forum_path)
        result = db.delete_message(message_id)
        if result:
            return "ураћено успешно"
        else:
            return "не може бити ураћено"
    else:
        return "то није твоја порука"


@app.route('/forum/<page_name>/<forum_id>', methods=['GET', 'POST'])
def view1(page_name,forum_id):
    if 'user' in session:
        db = DB(db_path)
        info1 = [session['user'], forum_id]
        has_read = db.is_that_readed(info1)
        if not has_read:
            db_forum = DB(db_forum_path)
            db_forum.popularity_add(info1)
            db.make_it_readed(info1)
        if request.method == 'POST':
            comment_text = request.form.get('comment')
            if comment_text:
                now = datetime.now()
                time = f"{now.hour}:{now.minute}:{now.day}:{now.month}:{now.year}"
                info1 = {
                    'username': session.get('user'),
                    'time': time,
                    'forum_name': page_name,
                    'message': comment_text
                }
                db = DB(db_forum_path)
                answer = db.add_messages_to_forum(info1)
                if answer != True:
                    return "грешка неможе да пошаљи поруку"
                return redirect(url_for('view1', page_name=page_name , forum_id=forum_id))
        db = DB(db_forum_path)
        # Загружаем первую страницу (page=0)
        info = list(db.get_messages(page_name, 0))
        return render_template('forum_view.html', page_name=page_name, forum_id=forum_id, forums=info)
    else:
        return redirect(url_for('register'))

# Новый маршрут для обработки AJAX-запросов
# В файле вашего основного приложения Flask
@app.route('/forum/<page_name>/ajax', methods=['POST'])
def ajax_handler(page_name):
    if 'user' in session:
        data = request.get_json()
        page = data.get('page', 0)
        print(page)
        db = DB(db_forum_path)
        special = True
        messages = db.get_messages(page_name, page ,special)
        return jsonify({'response_text': messages})
    else:
        return redirect(url_for('register'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        db = DB(db_path)  # Создаем экземпляр класса DB

        result = db.validate(username, password)
        if result == True:
            session['user'] = username  # Добавляем пользователя в сессию
            return redirect(url_for('home'))  # Перенаправляем на главную страницу
        else:
            return f"грешка у моменат улоза на налог"

    return render_template('login.html', text="уђи на налог")

# Выход
@app.route('/logout')
def logout():
    session.pop('user', None)   # Удаляем пользователя из сессии
    session.pop('avatar', None) # Удаляем аватар из сессии
    return redirect(url_for('login'))

@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    global data
    if 'user' in session:
        username = session.get('user')  # Получаем имя пользователя

        if len(data) == 0:
            data = {username: [0, datetime.day]}

        if username not in data:
            data[username] = [0, datetime.day]

        if data[username][0] <= 19:
            if request.method == 'POST':
                image = request.files.get('photo')
                text = request.form.get('text')
                task_type = request.form.get('taskType')  # Получаем тип задания

                if image and text and task_type:
                    # Получаем исходное расширение файла
                    file_extension = os.path.splitext(image.filename)[1]
                    # Создаём новое имя файла с текстом и исходным расширением
                    if base_dir != "D:\\windos_custom\\gdz.rs":
                        image_path = os.path.join("/home/sergeyeofjhgu/gdz.rs/uploads", f"{text}{file_extension}")
                    else:
                        image_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{text}{file_extension}")
                    image.save(image_path)

                    # Формируем сообщение для Telegram
                    message = (
                        f"Новый файл от пользователя {username}:\n"
                        f"Тип задания: {task_type}\n"
                        f"Информация: {text}"
                    )

                    # Отправляем сообщение и файл в Telegram
                    Telegramm_sent.send_text_to_me(message)  # Отправляем текстовое сообщение
                    Telegramm_sent.send_file_as_document(image_path, file_name=image.filename)  # Отправляем файл как документ

                    # Удаляем сохранённый файл
                    try:
                        os.remove(image_path)
                    except FileNotFoundError:
                        print(f"Фајл {image_path} не найден для удаления.")

                    # Обновляем счётчик публикаций
                    data[username][0] += 1
                    remaining = 20 - data[username][0]
                    return render_template_string(f"све добро ви можете да пустити јеш {remaining} домачи")
        else:
            # Обнуляем счётчик, если день изменился
            if data[username][1] != datetime.day:
                data[username][0] = 0
                return redirect(url_for('submit_homework'))
            else:
                return "данас ви сте публицирали 20 домачи поново публицираније ће радити сутра"
    else:
        return redirect(url_for('register'))

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
        return "Вы достигли лимита публикаций на сегодня. Попробуйте завтра."

    if request.method == 'POST':
        try:
            # Считываем данные формы
            topic = request.form.get('topic')
            title = request.form.get('title')
            additional_info = request.form.get('additional_info')
            school = request.form.get('school', 'None')  # Если школа не указана, устанавливаем 'None'

            if not topic or not title:  # Проверяем обязательные поля
                return "Тема и название обязательны для заполнения."

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
                return "Ошибка базы данных. Проверьте лог."

            # Увеличиваем счётчик публикаций
            forum_data[username][0] += 1

            return (f'Тема: {topic}<br>'
                    f'Название: {title}<br>'
                    f'Доп. информация: {additional_info}<br>'
                    f'Школа: {school}')
        except Exception as e:
            print(f"Ошибка: {e}")
            return "Произошла ошибка при обработке данных."

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
                    f"Дополнительная информация: Успешно отправлена в Telegram"
                )
            except Exception as e:
                print(f"Ошибка: {e}")
                return "Ошибка при обработке действия"
        else:
            return render_template('admin_panel.html')
    else:
        return render_template('404.html'), 404

@app.route('/for_me/create_account', methods=['POST'])
def create_account1():
    try:
        db = DB(db_system)
        data = request.get_json()
        user_ip = request.remote_addr

        if not data:
            return {"error": "Нет данных в запросе"}, 400

        encrypted_username = data.get("username")
        encrypted_password = data.get("password")

        print(f"Полученные данные (Base64 username): {encrypted_username}")
        print(f"Полученные данные (Base64 password): {encrypted_password}")

        if not encrypted_username or not encrypted_password:
            return {"error": "Не переданы зашифрованные данные"}, 400

        try:
            encrypted_username = b64decode(encrypted_username)
            encrypted_password = b64decode(encrypted_password)
        except Exception as e:
            print(f"Ошибка декодирования Base64: {e}")
            return {"error": "Некорректный формат зашифрованных данных"}, 400

        print(f"Декодированные данные (username): {encrypted_username}")
        print(f"Декодированные данные (password): {encrypted_password}")

        username = db.decrypt_user_data(user_ip, encrypted_username)
        password = db.decrypt_user_data(user_ip, encrypted_password)

        print(f"Расшифрованное имя пользователя: {username}")
        print(f"Расшифрованный пароль: {password}")

        if not isinstance(username, str) or not isinstance(password, str):
            print(f"Ошибка дешифровки: username={username}, password={password}")
            return {"error": "Ошибка при дешифровке данных"}, 400

        result = db.add_user_chat(username, password)
        if result:
            # Удаляем сессию после успешного создания аккаунта
            if db.remove_session_user(user_ip):
                print(f"Сессия для IP {user_ip} успешно удалена после создания аккаунта.")
            else:
                print(f"Не удалось удалить сессию для IP {user_ip}.")
            return {"message": "Аккаунт успешно создан"}, 200
        else:
            return {"error": "Ошибка при создании аккаунта"}, 500

    except Exception as e:
        print(f"Ошибка: {e}")
        return {"error": "Внутренняя ошибка сервера"}, 500


@app.route('/for_me/connect_session', methods=['POST'])
def connect_session():
    try:
        user_ip = request.remote_addr
        if user_ip:
            db = DB(db_system)
            crypto = Cryptography()
            private_key, public_key = crypto.generate_keys()

            # Сохранение ключей в базе
            public_key_pem = db.add_session_user(private_key, public_key, user_ip)

            if public_key_pem:
                return {"public_key": public_key_pem}, 200
            else:
                return {"error": "Не удалось создать сессию"}, 500
        else:
            return {"error": "IP-адрес не найден"}, 400
    except Exception as e:
        print(f"Ошибка: {e}")
        return {"error": "Произошла ошибка на сервере"}, 500



@app.route('/for_me/login', methods=['POST'])
def login1():
    try:
        db = DB(db_system)
        data = request.get_json()
        user_ip = request.remote_addr

        if not data:
            return {"error": "Нет данных в запросе"}, 400

        encrypted_username = data.get("username")
        encrypted_password = data.get("password")

        print(f"Полученные данные (Base64 username): {encrypted_username}")
        print(f"Полученные данные (Base64 password): {encrypted_password}")

        if not encrypted_username or not encrypted_password:
            return {"error": "Не переданы зашифрованные данные"}, 400

        try:
            encrypted_username = b64decode(encrypted_username)
            encrypted_password = b64decode(encrypted_password)
        except Exception as e:
            print(f"Ошибка декодирования Base64: {e}")
            return {"error": "Некорректный формат зашифрованных данных"}, 400

        print(f"Декодированные данные (username): {encrypted_username}")
        print(f"Декодированные данные (password): {encrypted_password}")

        username = db.decrypt_user_data(user_ip, encrypted_username)
        password = db.decrypt_user_data(user_ip, encrypted_password)

        print(f"Расшифрованное имя пользователя: {username}")
        print(f"Расшифрованный пароль: {password}")

        if not isinstance(username, str) or not isinstance(password, str):
            print(f"Ошибка дешифровки: username={username}, password={password}")
            return {"error": "Ошибка при дешифровке данных"}, 400

        result = db.login_user_chat(username, password)
        if result:
            return {"message": "Успешный вход"}, 200
        else:
            return {"error": "Неверное имя пользователя или пароль"}, 400

    except Exception as e:
        print(f"Ошибка: {e}")
        return {"error": "Внутренняя ошибка сервера"}, 500


@app.errorhandler(404)
def page_not_found(e):
    # Можно вернуть кастомный HTML или шаблон
    return render_template('404.html', text=request.path), 404

# Запуск приложения
if __name__ == '__main__':
    app.run(debug=True)