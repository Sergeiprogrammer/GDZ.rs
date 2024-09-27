import json
import time
import os

# это чтобы тебе после того как в вайбер отправят учебник ты бы мог заполнить json информацию о нём

def add_book_info(filename):
    # Ввод информации о книге
    num_pages = int(input("Введите количество страниц: "))
    author_status = input("Введите статус автора: ")

    # Словарь для хранения количества заданий на каждой странице
    page_tasks = {}

    value = False
    for page in range(1, num_pages + 1):
        if value:
            pass
        else:
            print("Введите от какого по какое задание на странице обьяснение например на странице 11 находять 8 9 и 10 значит нужно написать 8-10 ")
        tasks = (input(f"Введите от какого по какое задание на странице {page}: "))
        page_tasks[str(page)] = tasks

    # Создание структуры данных для JSON
    book_info = {
        "учебник или домашка или вежбанка": num_pages,
        "Статус автора": author_status,
        "есть ли ответы": page_tasks
    }

    # Запись данных в JSON файл
    with open(filename, 'w', encoding='utf-8') as file:
        json.dump(book_info, file, ensure_ascii=False, indent=4)
    print(f"Информация о книге успешно сохранена в файл {filename}")


# Основная часть программы
if __name__ == "__main__":
    filename = "info.json"
    add_book_info(filename)