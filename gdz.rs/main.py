from flask import Flask, render_template, render_template_string
import os
app = Flask(__name__)

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

@app.route('/predmet/<ime>/<int:razred>/<ucbenik>')
def show_razred1(ime, razred , ucbenik):
    with open(f'D:\\windos_custom\\gdz.rs\\static\\{ime}\\{razred}\\{ucbenik}\\about.txt', 'r', encoding='utf-8') as file:
        # Читаем все содержимое файла в строку
        content = file.read()
    return content

@app.route('/predmet/<ime>/<int:razred>')
def show_razred(ime, razred):
    info = []
    icons = []
    base_dir = "D:\\windos_custom\\gdz.rs"
    static_dir = os.path.join(base_dir, "static", "matematika", "8")

    for paths, directories, files in os.walk(static_dir):
        if "images" not in paths:
            # Append the full path to the info list
            info.append(os.path.basename(paths))
            # Get the relative path starting from the root directory
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

if __name__ == '__main__':
    app.run(debug=True)
