import zipfile
import os
import shutil

zip_file_path = '/home/sergeyeofjhgu/gdz.rs/static/english (2).zip'
extract_to_path = '/home/sergeyeofjhgu/gdz.rs/static/'

# Открытие и извлечение содержимого
with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
    zip_ref.extractall(extract_to_path)

print("Файлы успешно извлечены!")

# Укажите пути исходной и конечной папок
source_dir = "/home/sergeyeofjhgu/gdz.rs/static/english"
destination_dir = "/home/sergeyeofjhgu/gdz.rs/static/"

# Перенос всех папок из source_dir в destination_dir
for item in os.listdir(source_dir):
    source_path = os.path.join(source_dir, item)
    destination_path = os.path.join(destination_dir, item)

    # Проверяем, является ли объект папкой
    if os.path.isdir(source_path):
        shutil.move(source_path, destination_path)
        print(f"Папка {source_path} успешно перемещена в {destination_path}")

print("Все папки успешно перемещены!")
