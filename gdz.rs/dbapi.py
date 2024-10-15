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

    def create_forum(self,info):
        conn = sqlite3.connect(self.db_name)
        try:
            cursor = conn.cursor()

            # SQL запрос для вставки данных
            cursor.execute("""
                INSERT INTO forum (topic, title, additional_info, school, author_name, popularity) 
                VALUES (?, ?, ?, ?, ?, ?)
            """, (info['topic'], info['title'], info['additional_info'], info.get('school', 'None'), info['author_name'],info['popularity']))

            # Зафиксировать изменения
            conn.commit()
            conn.close()

            return "Успешно добавлено"
        except Exception as e:
            print(f"Ошибка: {e}")
            return "405"
        finally:
            conn.close()

    def create_question(self, info):
        conn = sqlite3.connect(self.db_name)
        try:
            cursor = conn.cursor()

            # SQL запрос для вставки данных
            cursor.execute("""
                   INSERT INTO question (question, title) 
                   VALUES (?, ?, ?, ?)
               """, (info['topic'], info['title'], info['author_name'],info['popularity']))

            # Зафиксировать изменения
            conn.commit()
            conn.close()

            return "Успешно добавлено"
        except Exception as e:
            print(f"Ошибка: {e}")
            return "405"
        finally:
            conn.close()

    def get_status(self, info):
        conn = sqlite3.connect(self.db_name)
        try:
            cursor = conn.cursor()
            cursor.execute("""
                                    SELECT * FROM forum
                                    ORDER BY popularity DESC
                                    LIMIT ? OFFSET ?
                                """, (50, info*50))
            top_users = cursor.fetchall()  # Сохраняем результат в переменную
            if len(top_users) != 0:
                return top_users
            else:
                return ""
        finally:
            conn.close()

    def get_messages(self, info):
        conn = sqlite3.connect(self.db_name)
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT Author_name, time, forum_name, message FROM forum_messages WHERE forum_name = ?",
                           (info,))
            result = cursor.fetchall()  # Сохраняем результат в переменную
            if len(result) > 0:
                return result
            else:
                return 'ништа'
        except Exception as e:
            return [str(e), "text", "text", "text"]
        finally:
            conn.commit()
            conn.close()

    def add_messages_to_forum(self, info):
        conn = sqlite3.connect(self.db_name)
        try:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO forum_messages (Author_name, time, forum_name, message) 
                VALUES (?, ?, ?, ?)
            """, (info['username'], info['time'], info['forum_name'], info['message']))
            conn.commit()
            return True
        except Exception as e:
            # Log the error message
            print(f"Database error: {e}")
            return False
        finally:
            conn.close()



