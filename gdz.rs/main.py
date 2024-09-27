from flask import Flask, render_template, render_template_string, session, redirect, request, url_for
import os
from dbapi import DB
app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Set a secret key for sessions

sigma = []

@app.route('/')
def home():
    return render_template("index.html")

@app.route('/about.txt')
def about():
    return render_template("about.txt.html")

@app.route('/predmet/<ime>')
def class1(ime):
    return render_template("select class.html", ime=ime)

@app.route('/predmet/<ime>/<int:razred>/<ucbenik>/<homework_name>')
def show_home_work(ime, razred, ucbenik, homework_name):
    base_dir = "D:\\windos_custom\\gdz.rs"
    static_dir = os.path.join(base_dir, "static", ime, str(razred), ucbenik, "images" , homework_name)
    relative_path = os.path.relpath(static_dir, base_dir)
    web_path = relative_path.replace("\\", "/") + ".jpg"
    print(web_path)
    return render_template("show_home_work.html" , image=web_path)

@app.route('/predmet/<ime>/<int:razred>/<ucbenik>')
def show_home_works(ime, razred, ucbenik):
    image_info = []
    base_dir = "D:\\windos_custom\\gdz.rs"
    static_dir = os.path.join(base_dir, "static", ime, str(razred), ucbenik, "images")
    relative_path = os.path.relpath(static_dir, base_dir)
    for paths, directories, files in os.walk(static_dir):
        for i in files:
            path = relative_path.replace("\\", "/") + "/" + i
            image_info.append((path, i[0:-4]))  # Use filename as info_item
    return render_template("all_home_works.html", image_info=image_info, ime=ime, razred=razred , ucbenik=ucbenik)

@app.route('/predmet/<ime>/<int:razred>')
def show_razred(ime, razred):
    info = []
    icons = []
    base_dir = "D:\\windos_custom\\gdz.rs"
    static_dir = os.path.join(base_dir, "static", ime, str(razred))

    for paths, directories, files in os.walk(static_dir):
        if "images" not in paths:
            info.append(os.path.basename(paths))
            relative_path = os.path.relpath(paths, base_dir)
            web_path = relative_path.replace("\\", "/")
            icons.append(f"{web_path}/Icon.jpg")

    if icons:
        # Remove the first element if necessary (adjust both lists)
        icons.pop(0)
        info.pop(0)

    # Zip the icons and info lists together
    image_info = list(zip(icons, info))
    print(image_info)
    return render_template("all_books.html", image_info=image_info , ime=ime , razred=razred)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        avatar = request.files.get('image_file')

        db = DB('main.db')  # Create an instance of DB

        result = db.add_user(username, password)
        if username and password and result == True:
            session['user'] = username

            # Handle avatar if needed...

            return redirect(url_for('login'))
        else:
            return f"Ошибка при регистрации: {result}"
    return render_template('create_account.html' , text = "регестрациja")

@app.route('/forum',  methods=['GET', 'POST'])
def forum():
    if 'user' in session:
        return render_template("forum.html")
    else:
        return redirect(url_for('register'))  # Added 'return' statement

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        db = DB('main.db')  # Создаем экземпляр класса DB

        result = db.validate(username, password)
        if result == True:
            session['user'] = username  # Добавляем пользователя в сессию
            return redirect(url_for('home'))  # Перенаправляем на главную страницу
        else:
            return f"Ошибка входа: {result}"

    return render_template('login.html', text="Вход в аккаунт")


@app.route('/logout')
def logout():
    session.pop('user', None)  # Удаляем пользователя из сессии
    session.pop('avatar', None)  # Удаляем аватар из сессии
    return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(debug=True)
