import sqlite3

def init_db(db_name):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            status_of_ban BOOLEAN DEFAULT 0,
            admin_rights BOOLEAN DEFAULT 0,
            money BOOLEAN DEFAULT 0
        )
    ''')
    conn.commit()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users_info (
            username TEXT,
            readed_forums_id INTEGER
        )
    ''')
    conn.commit()
    conn.close()
    print(f"База данных '{db_name}' успешно инициализирована.")

def init_second(db_name):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    # Создание таблицы forum
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS forum (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            topic TEXT,
            title TEXT,
            additional_info TEXT,
            school TEXT,
            author_name TEXT NOT NULL,
            popularity_week INTEGER,
            popularity_all_time INTEGER
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS forum_messages (
            Author_name TEXT,
            time TEXT,
            forum_name TEXT,
            message TEXT,
            id INTEGER PRIMARY KEY AUTOINCREMENT
        )
    ''')

    # Исправленное создание таблицы question
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS question (
            question TEXT NOT NULL,
            title TEXT NOT NULL,
            author_name TEXT NOT NULL,
            popularity INTEGER
        )
    ''')
    conn.commit()
    conn.close()
    print(f"База данных '{db_name}' успешно инициализирована.")

def init_third(db_name):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS date_of_drop_week_popylarity (
            days_left INTEGER
        )
    ''')
    conn.commit()
    conn.close()
    print(f"База данных '{db_name}' успешно инициализирована.")

def init_fourth(db_name):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sesion (
            private_key TEXT,
            public_key INTEGER,
            user_ip TEXT
        )
    ''')


    cursor.execute('''
        CREATE TABLE IF NOT EXISTS chat (
            sender_id TEXT,
            reciver_id INTEGER,
            message_text TEXT
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS accounts (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT, -- Автоматический инкремент ID
            username TEXT NOT NULL,
            password TEXT NOT NULL,
            sesion_key TEXT,
            time_of_get_acces TEXT
        )
    ''')
    conn.commit()
    conn.close()
    print(f"База данных '{db_name}' успешно инициализирована.")


if __name__ == '__main__':
    init_db('main.db')
    init_second('forum.db')
    init_third('system.db')
    init_fourth('chat.db')