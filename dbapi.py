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
                INSERT INTO forum (topic, title, additional_info, school, author_name, popularity_week, popularity_all_time) 
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (info['topic'], info['title'], info['additional_info'], info.get('school', 'None'), info['author_name'] , 0 , 0))

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
            cursor.execute("SELECT * FROM forum ORDER BY popularity_week DESC")
            top_users = cursor.fetchall()  # Сохраняем результат в переменную
            if len(top_users) != 0:
                return top_users
            else:
                return ""
        finally:
            conn.close()

    # В файле dbapi.py

    def get_messages(self, forum_name, page , specila = None):
        conn = sqlite3.connect(self.db_name)
        try:
            cursor = conn.cursor()
            batch_size = 50
            offset = page * batch_size
            if specila:
                cursor.execute(
                    "SELECT Author_name, time, forum_name, id, message FROM forum_messages WHERE forum_name = ? LIMIT ? OFFSET ?",
                    (forum_name, 103, page*103))
            else:
                cursor.execute(
                    "SELECT Author_name, time, forum_name, id, message FROM forum_messages WHERE forum_name = ? LIMIT ? OFFSET ?",
                    (forum_name, 103, 0))
            result = cursor.fetchall()
            return result if result else []
        except Exception as e:
            print(f"Ошибка при получении сообщений: {e}")
            return []
        finally:
            conn.close()

    def delete_message(self, info):
        conn = sqlite3.connect(self.db_name)
        try:
            cursor = conn.cursor()
            # Удаление сообщения с ID, равным info
            cursor.execute("DELETE FROM forum_messages WHERE id = ?", (info,))
            return "Message deleted successfully"
        except Exception as e:
            return f"An error occurred: {e}"
        finally:
            conn.commit()
            conn.close()
            # Закрытие соединения с базой данных

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

    def popularity_add(self, info):
        conn = sqlite3.connect(self.db_name)
        try:
            cursor = conn.cursor()
            # Попытка обновить существующую запись
            cursor.execute('''
                UPDATE forum
                SET popularity_week = popularity_week + 1,
                    popularity_all_time = popularity_all_time + 1
                WHERE id = ?
            ''', (info[1],))

            conn.commit()
        except Exception as e:
            print(f"Ошибка при обновлении популярности: {e}")
        finally:
            conn.close()

    def is_that_readed(self, info):
        conn = sqlite3.connect(self.db_name)
        try:
            cursor = conn.cursor()
            # Если запись уже существует, увеличиваем views на 1
            cursor.execute("SELECT * FROM users_info WHERE username = ? AND readed_forums_id = ?" , (info[0], info[1]))
            if cursor.fetchone():
                return True
            else:
                return False
        except Exception as e:
            print(f"Ошибка при обновлении популярности: {e}")
        finally:
            conn.close()

    def make_it_readed(self, info):
        conn = sqlite3.connect(self.db_name)
        try:
            cursor = conn.cursor()
            # Вставляем запись о прочтении форума пользователем
            cursor.execute('''
                INSERT INTO users_info (username, readed_forums_id)
                VALUES (?, ?)
            ''', (info[0], info[1]))
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            # Если запись уже существует (если есть уникальные ограничения)
            return False
        except Exception as e:
            print(f"Ошибка при добавлении прочтения форума: {e}")
            return False
        finally:
            conn.close()

    def check_for_ban(self, info):
        conn = sqlite3.connect(self.db_name)
        try:
            cursor = conn.cursor()
            # Проверяем наличие пользователя с заданным username и статусом бана
            cursor.execute("SELECT * FROM users WHERE status_of_ban = 1 AND username = ?", (info,))
            if cursor.fetchone():  # Если пользователь найден, возвращаем True
                return True
            else:  # Если пользователь не найден, возвращаем False
                return False
        except Exception as e:
            print(f"Ошибка при проверке пользователя: {e}")
        finally:
            conn.close()
