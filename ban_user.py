import sqlite3
import os

# Путь к базе данных
base_dir = os.path.join("/", 'home', 'sergeyeofjhgu', 'gdz.rs')
db_path = os.path.join(base_dir, 'main.db')

def choice():
    while True:
        try:
            user_choice = int(input("Забанить или разбанить (1 - забанить, 2 - разбанить, 3 - выдать привилегии, 4 - снять привилегии, 5 - дать деньги, 6 - убрать деньги 0 - выйти): "))
            if user_choice == 1:
                ban(1)
            elif user_choice == 2:
                ban(0)
            elif user_choice == 3:
                make_admin(1)
            elif user_choice == 4:
                make_admin(0)
            elif user_choice == 5:
                give_money(1)
            elif user_choice == 6:
                give_money(0)
            elif user_choice == 0:
                print("Выход из программы.")
                break
            else:
                print("Введите 1, 2 или 0.")
        except ValueError:
            print("Введите число, а не символ.")

def ban(value):
    # Подключение к базе данных
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        username = input("Введите имя человека для {'бана' if value == 1 else 'разбана'}")

        # Обновление статуса бана
        try:
            cursor.execute("UPDATE users SET status_of_ban = {value} WHERE username = ?", (username,))
            if cursor.rowcount == 0:
                print(f"Пользователь '{username}' не найден.")
            else:
                print(f"Пользователь '{username}' успешно {'забанен' if value == 1 else 'разбанен'}.")
            conn.commit()
        except Exception as e:
            print(f"Ошибка при обновлении статуса бана: {e}")

def make_admin(value):
    # Подключение к базе данных
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        username = input(f"Введите имя человека для {'выдачи' if value == 1 else 'снятия'} привилегии: ")

        # Обновление статуса бана
        try:
            cursor.execute(f"UPDATE users SET admin_rights = {value} WHERE username = ?", (username,))
            if cursor.rowcount == 0:
                print(f"Пользователь '{username}' не найден.")
            else:
                print(f"Пользователь '{username}' успешно {'получил' if value == 1 else 'лешился'} привелегии")
            conn.commit()
        except Exception as e:
            print(f"Ошибка при обновлении статуса бана: {e}")

def give_money(value):
    # Подключение к базе данных
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        username = input(f"Введите имя человека для {'выдачи' if value == 1 else 'снятия'} денег: ")
        money = int(input(f"введите количество денег которое хотите выдать если хотите отнять напишите 0"))
        # Обновление статуса бана
        try:
            cursor.execute(f"UPDATE users SET money = {money} WHERE username = ?", (username,))
            if cursor.rowcount == 0:
                print(f"Пользователь '{username}' не найден.")
            else:
                print(f"Пользователь '{username}' успешно {'получил' if value == 1 else 'лешился'} денег")
            conn.commit()
        except Exception as e:
            print(f"Ошибка при обновлении статуса бана: {e}")

# Запуск программы
choice()