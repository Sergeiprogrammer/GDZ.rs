import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
import uuid
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization, hashes
from crypto_utils import Cryptography
import json

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

            return "Успешно добавлено"
        except sqlite3.Error as e:  # Используем конкретное исключение
            print(f"Ошибка базы данных: {e}")
            return "405"
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
            return "Успешно добавлено"
        except Exception as e:
            print(f"Ошибка: {e}")
            return "Произошла ошибка при добавлении вопроса."
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

    # не главный функционал сайта а чатсь твоего мессенджера (ссылка на гитхаб)
    def add_user_chat(self, username, password):
        conn = sqlite3.connect(self.db_name)
        try:
            cursor = conn.cursor()
            # Проверяем, существует ли пользователь с таким именем
            cursor.execute("SELECT 1 FROM accounts WHERE username = ?", (str(username),))
            if cursor.fetchone():
                return "Пользователь с таким именем уже существует в системе!"
            else:
                # Хешируем пароль перед сохранением
                hashed_password = generate_password_hash(str(password))
                cursor.execute('''
                    INSERT INTO accounts (username, password, sesion_key)
                    VALUES (?, ?, ?)
                ''', (str(username), hashed_password, None))
                conn.commit()
                return True
        except sqlite3.IntegrityError:
            return "Пользователь с таким именем уже существует."
        except Exception as e:
            print(f"Ошибка при добавлении пользователя: {e}")
            return "Произошла ошибка при добавлении пользователя."
        finally:
            conn.close()


    def add_session_user(self, private_key, public_key, user_ip):
        conn = sqlite3.connect(self.db_name)
        try:
            cursor = conn.cursor()

            # Сериализация ключей в PEM-формат
            private_key_pem = private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.TraditionalOpenSSL,
                encryption_algorithm=serialization.NoEncryption()
            ).decode()  # Преобразуем байты в строку

            public_key_pem = public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            ).decode()

            # Вставка данных в базу
            cursor.execute('''
                INSERT INTO sesion (private_key, public_key, user_ip)
                VALUES (?, ?, ?)
            ''', (private_key_pem, public_key_pem, user_ip))
            conn.commit()
            return public_key_pem  # Возвращаем публичный ключ
        except sqlite3.IntegrityError:
            return "Пользователь с таким IP уже существует."
        except Exception as e:
            print(f"Ошибка при добавлении пользователя: {e}")
            return None
        finally:
            conn.close()

    def remove_session_user(self, user_ip):
        conn = sqlite3.connect(self.db_name)
        try:
            cursor = conn.cursor()
            # Удаление записи сессии для данного IP
            cursor.execute('DELETE FROM sesion WHERE user_ip = ?', (user_ip,))
            conn.commit()
            print(f"Сессия для IP {user_ip} успешно удалена.")
            return True
        except Exception as e:
            print(f"Ошибка при удалении сессии: {e}")
            return False
        finally:
            conn.close()


    def login_user_chat(self, username, password):
        conn = sqlite3.connect(self.db_name)
        try:
            cursor = conn.cursor()
            # Проверяем пароль для указанного пользователя
            cursor.execute("SELECT password FROM accounts WHERE username = ?", (username,))
            result = cursor.fetchone()

            if result and check_password_hash(result[0], password):
                # Генерируем новый сессионный ключ
                session_key = str(uuid.uuid4())

                # Обновляем сессионный ключ в базе данных
                cursor.execute('''
                    UPDATE accounts
                    SET sesion_key = ?
                    WHERE username = ?
                ''', (session_key, username))
                conn.commit()

                return f"Успешный вход в аккаунт! Ваш ключ: {session_key}"
            else:
                return "Неправильное имя пользователя или пароль."
        except Exception as e:
            # Логирование ошибки
            print(f"Ошибка при проверке пользователя: {e}")
            return "Произошла ошибка при проверке пользователя."
        finally:
            conn.close()

    def decrypt_user_data(self, user_ip, data):
        conn = sqlite3.connect(self.db_name)
        try:
            cursor = conn.cursor()
            cursor.execute('SELECT private_key FROM sesion WHERE user_ip = ?', (user_ip,))
            result = cursor.fetchone()

            if not result:
                return {"error": "Сессия для данного IP не найдена"}

            private_key_pem = result[0]

            private_key = serialization.load_pem_private_key(
                private_key_pem.encode(),
                password=None
            )

            # Проверяем тип данных
            if not isinstance(data, bytes):
                print(f"Ошибка: данные должны быть в формате bytes. Текущий тип: {type(data)}")
                return {"error": "Данные не являются байтами"}

            crypto = Cryptography()
            decrypted_data = crypto.decrypt_data(private_key, data)

            print(f"Расшифрованные данные: {decrypted_data}")
            return decrypted_data
        except Exception as e:
            print(f"Ошибка при дешифровке данных: {e}")
            return {"error": "Произошла ошибка при дешифровке данных"}
        finally:
            conn.close()




