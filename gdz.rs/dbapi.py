import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

class DB:
    def __init__(self, db_name):
        self.db_name = db_name

    def add_user(self, username, password):
        conn = sqlite3.connect(self.db_name)
        try:
            cursor = conn.cursor()
            # Проверяем, существует ли пользователь с таким именем
            cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
            if cursor.fetchone():
                return "Пользователь с таким именем уже существует в системе!"
            else:
                # Хешируем пароль перед сохранением
                hashed_password = generate_password_hash(password)
                cursor.execute('''
                    INSERT INTO users (username, password)
                    VALUES (?, ?)
                ''', (username, hashed_password))
                conn.commit()
                return True
        except sqlite3.IntegrityError:
            return "Пользователь с таким именем уже существует."
        except Exception as e:
            # Логирование ошибки
            print(f"Ошибка при добавлении пользователя: {e}")
            return "Произошла ошибка при добавлении пользователя."
        finally:
            conn.close()

    def validate(self, username, password):
        conn = sqlite3.connect(self.db_name)
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT password FROM users WHERE username = ?", (username,))
            result = cursor.fetchone()
            if result and check_password_hash(result[0], password):
                return True
            else:
                return "Неправильное имя пользователя или пароль"
        except Exception as e:
            # Логирование ошибки
            print(f"Ошибка при проверке пользователя: {e}")
            return "Произошла ошибка при проверке пользователя."
        finally:
            conn.close()
