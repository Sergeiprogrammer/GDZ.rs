import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
from email_module import Email
import random

class DB:
    def __init__(self, db_name):
        self.db_name = db_name

    def add_user(self, username, password, email):
        conn = sqlite3.connect(self.db_name)
        try:
            cursor = conn.cursor()
            # Проверяем, существует ли пользователь с таким именем
            cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
            if cursor.fetchone():
                return "човек са истим именом постоји на сајту"

            # Проверяем, существует ли email
            cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
            if cursor.fetchone():
                return "човек са истим email постоји на сајту"

            else:
                # Хешируем пароль перед сохранением
                hashed_password = generate_password_hash(password)
                cursor.execute('''
                    INSERT INTO users (username, password, email)
                    VALUES (?, ?, ?)
                ''', (username, hashed_password, email))
                conn.commit()
                return True
        except sqlite3.IntegrityError:
            return "човек са истим именом или email постоји на сајту"
        except Exception as e:
            # Логирование ошибки
            print(f"Ошибка при добавлении пользователя: {e}")
            return "грешка на серверу"
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
                return "неправилно име корисника или лозинка"
        except Exception as e:
            # Логирование ошибки
            print(f"Ошибка при проверке пользователя: {e}")
            return "грешка у валидације корисника"
        finally:
            conn.close()

    def create_forum(self, info):
        conn = sqlite3.connect(self.db_name)
        try:
            cursor = conn.cursor()

            # SQL запрос для вставки данных
            cursor.execute("""
                INSERT INTO forum (topic, title, additional_info, school, author_name, popularity_week, popularity_all_time)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (info['topic'], info['title'], info['additional_info'], info['school'], info['author_name'], 0, 0))

            # Фиксируем изменения
            conn.commit()

            return "Успешно направлијен форум"
        except sqlite3.Error as e:  # Используем конкретное исключение
            print(f"Ошибка базы данных: {e}")
            return "грешка на серверу"
        finally:
            conn.close()


    def create_question(self, info):
        conn = sqlite3.connect(self.db_name)
        try:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO question (question, title, author_name, popularity)
                VALUES (?, ?, ?, ?)
            """, (info['topic'], info['title'], info['author_name'], info['popularity']))
            conn.commit()
            return "Успешно додано питаније"
        except Exception as e:
            print(f"Ошибка: {e}")
            return "грешка на серверу"
        finally:
            conn.close()

    def get_status(self, info):
        conn = sqlite3.connect(self.db_name)
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM forum ORDER BY popularity_week DESC LIMIT ? OFFSET ?",(103, info*103))
            top_users = cursor.fetchall()  # Сохраняем результат в переменную
            if len(top_users) != 0:
                return top_users
            else:
                return "грешка на серверу"
        finally:
            conn.close()


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
            return f"грешка на серверу"
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

    def check_user_ban(self, username):
        conn = sqlite3.connect(self.db_name)
        try:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT status_of_ban
                FROM users
                WHERE username = ? AND status_of_ban = 1
            ''', (username,))
            result = cursor.fetchone()
            return result is not None
        except Exception as e:
            print(f"Ошибка при проверке блокировки пользователя: {e}")
            return False
        finally:
            conn.close()

    def validate_rights(self, username):
        conn = sqlite3.connect(self.db_name)
        try:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT admin_rights
                FROM users
                WHERE username = ? AND admin_rights = 1
            ''', (username,))
            result = cursor.fetchone()
            return result is not None
        except Exception as e:
            print(f"Ошибка при проверке блокировки пользователя: {e}")
            return False
        finally:
            conn.close()

    def give_money(self, username):
        conn = sqlite3.connect(self.db_name)
        try:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT money
                FROM users
                WHERE username = ?
            ''', (username,))
            result = cursor.fetchone()[0]
            return result
        except Exception as e:
            print(f"Ошибка при проверке блокировки пользователя: {e}")
            return False
        finally:
            conn.close()

    def get_link_to_info(self, razred, predmet):
        conn = sqlite3.connect(self.db_name)
        try:
            cursor = conn.cursor()

            # Проверяем, существует ли предмет в базе
            cursor.execute("PRAGMA table_info(main)")
            existing_columns = {row[1] for row in cursor.fetchall()}

            if predmet not in existing_columns:
                print(f"Предмет '{predmet}' не найден в таблице.")
                return "грешка на серверу"

            # Корректный SQL-запрос с format() для подстановки имени столбца
            cursor.execute(f"SELECT \"{predmet}\" FROM main WHERE razred = ?", (razred,))
            result = cursor.fetchone()

            return result[0] if result and result[0] else "грешка на серверу"

        except Exception as e:
            print(f"Ошибка при запросе к базе: {e}")
            return "грешка на серверу"

        finally:
            conn.close()

    def give_teacher_rights(self, username, teacher_code, code_db, usernames_db):
        # Шаг 1: Проверяем, существует ли указанный код в базе с кодами
        try:
            conn_codes = sqlite3.connect(code_db)
            cursor_codes = conn_codes.cursor()
            cursor_codes.execute("SELECT codes FROM date_of_drop_week_popylarity WHERE codes = ?", (teacher_code,))
            code_row = cursor_codes.fetchone()
        except Exception as e:
            print(f"Ошибка при запросе к базе кодов: {e}")
            return "грешка на стране сервера"
        finally:
            conn_codes.close()

        if not code_row:
            print("Код не найден в базе.")
            return "овај код није постоји"

        # Шаг 2: Если код найден, выдаём права преподавателя пользователю
        try:
            conn_users = sqlite3.connect(usernames_db)
            cursor_users = conn_users.cursor()
            cursor_users.execute("UPDATE users SET teacher_rights = 1 WHERE username = ?", (username,))
            cursor_users.execute("DELETE FROM date_of_drop_week_popylarity WHERE codes = ?", (teacher_code,))
            conn_users.commit()

            if cursor_users.rowcount == 0:
                print("Пользователь не найден в базе пользователей.")
                return "ваше име није постоје на сајту"
            else:
                print("Права преподавателя успешно выданы.")
                return "операција урађена успешно ви имате могуђност да користите привилегија наставни/ка,ци"
        except Exception as e:
            print(f"Ошибка при обновлении базы пользователей: {e}")
            return "грешка"
        finally:
            conn_users.close()

    def validate_teacher_rights(self, username):
        conn = sqlite3.connect(self.db_name)
        try:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT teacher_rights
                FROM users
                WHERE username = ? AND teacher_rights = 1
            ''', (username,))
            result = cursor.fetchone()
            return result is not None
        except Exception as e:
            print(f"Ошибка при проверке блокировки пользователя: {e}")
            return False
        finally:
            conn.close()