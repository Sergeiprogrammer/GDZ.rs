from flask import Flask, render_template, render_template_string, session, redirect, request, url_for
import os
import platform
from pathlib import Path
from dbapi import DB

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Задайте секретный ключ для сессий (замените на безопасный ключ в продакшене)

# Определение операционной системы для установки базового каталога
if platform.system() == 'Windows':
    base_dir = "D:\\windos_custom\\gdz.rs"
    db_path = 'main.db'
else:
    base_dir = '/home/sergeyeofjhgu/GDZ.rs/'
    db_path = '/home/sergeyeofjhgu/GDZ.rs/main.db'
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
@app.route('/forum', methods=['GET', 'POST'])
def forum():
    if 'user' in session:
        return render_template("forum.html")
    else:
        return redirect(url_for('register'))

# Вход
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

# Запуск приложения
if __name__ == '__main__':
    app.run(debug=True)
