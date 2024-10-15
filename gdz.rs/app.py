from flask import Flask, render_template, render_template_string, session, redirect, request, url_for
import os
import platform
from pathlib import Path
from dbapi import DB
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Задайте секретный ключ для сессий (замените на безопасный ключ в продакшене)

# Определение операционной системы для установки базового каталога
if platform.system() == 'Windows':
    base_dir = "D:\\windos_custom\\gdz.rs"
    db_path = 'main.db'
    db_forum_path = 'forum.db'
else:
    base_dir = '/home/sergeyeofjhgu/GDZ.rs/'
    db_path = '/home/sergeyeofjhgu/GDZ.rs/main.db'
    db_forum_path = '/home/sergeyeofjhgu/GDZ.rs/forum.db'
sigma = []

# Главная страница
@app.route('/')
def home():
    return render_template("index.html")

# Страница "О нас"
@app.route('/about.txt')
def about():
    return render_template("about.txt.html")

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

    for paths, directories, files in os.walk(static_dir):
        if "images" not in paths:
            info.append(os.path.basename(paths))
            relative_path = os.path.relpath(paths, base_dir)
            web_path = Path(relative_path).as_posix()
            icons.append(f"{web_path}/Icon.jpg")
            information.append(f"{paths}\info.txt")

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

        result = db.add_user(username, password)
        if username and password and result == True:
            session['user'] = username

            # Обработка аватара при необходимости...

            return redirect(url_for('login'))
        else:
            return f"Ошибка при регистрации: {result}"
    return render_template('create_account.html', text="Регистрация")

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

@app.route('/forum/<page_name>', methods=['GET', 'POST'])
def view1(page_name):
    if request.method == 'POST':
        comment_text = request.form.get('comment')
        if comment_text:
            # Save the comment to the database
            now = datetime.now()
            time = f"{now.hour}:{now.minute}:{now.day}:{now.month}:{now.year}"
            info1 = {
                'username': session.get('user'),
                'time': time,
                'forum_name': page_name,
                'message': comment_text
            }
            db = DB(db_forum_path)
            print(info1)
            answer = db.add_messages_to_forum(info1)
            if answer != True:
                return "Ошибка: не могу записать сообщение."
            # Redirect to the same page to prevent form resubmission
            return redirect(url_for('view1', page_name=page_name))
    # Handle GET request or after redirect
    db = DB(db_forum_path)
    info = list(db.get_messages(page_name))
    print(info)
    return render_template('forum_view.html', page_name=page_name, forums=info)

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
            return f"Ошибка входа: {result}"

    return render_template('login.html', text="Вход в аккаунт")

# Выход
@app.route('/logout')
def logout():
    session.pop('user', None)   # Удаляем пользователя из сессии
    session.pop('avatar', None) # Удаляем аватар из сессии
    return redirect(url_for('login'))

@app.route('/submit-homework')
def submit_homework():
    return render_template('homework_sent.html')

@app.route('/create_forum', methods=['GET', 'POST'])
def create_forum():
    if request.method == 'POST':
        # Обрабатываем данные формы
        try:
            topic = request.form.get('topic')
            title = request.form.get('title')
            additional_info = request.form.get('additional_info')
            school = request.form.get('school')

            if not school:
                school = 'None'

            info = {
                'topic': topic,
                'title': title,
                'additional_info': additional_info,
                'school': school,
                'author_name': session.get('user'),
                'popularity': 1488
            }

            db = DB(db_forum_path)
            db.create_forum(info)
            # Выводим данные в консоль для отладки
            print(f'Тема: {topic}')
            print(f'Название: {title}')
            print(f'Доп. информация: {additional_info}')
            print(f'Школа: {school}')
            return f'Тема: {topic}<br>Название: {title}<br>Доп. информация: {additional_info}<br>Школа: {school}'
        except:
            return "грешка има"
    else:
        # Если метод GET — отображаем форму
        return render_template('create_forum.html')

@app.route('/create_question', methods=['GET', 'POST'])
def create_forum_question():
    if request.method == 'POST':
        # Обрабатываем данные формы
        try:
            topic = request.form.get('topic')
            title = request.form.get('title')

            info = {
                'topic': topic,
                'title': title,
                'author_name': session.get('user'),
                'popularity': 0
            }

            db = DB(db_forum_path)
            db.create_question(info)
            # Выводим данные в консоль для отладки
            print(f'Тема: {topic}')
            print(f'Название: {title}')
            return f'Тема: {topic}<br>Название: {title}<br>Доп. информация:'
        except:
            return "грешка има"
    else:
        # Если метод GET — отображаем форму
        return render_template('create question.html')


# Запуск приложения
if __name__ == '__main__':
    app.run(debug=True)