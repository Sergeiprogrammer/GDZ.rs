import sqlite3

def init_db(db_name):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

def init_second(db_name):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    # Создание таблицы forum
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS forum (
            topic TEXT,
            title TEXT,
            additional_info TEXT,
            school TEXT,
            author_name TEXT NOT NULL, 
            popularity INTEGER
        )
    ''')

    cursor.execute('''
            CREATE TABLE IF NOT EXISTS forum_messages (
                Author_name TEXT,
                time TEXT,
                forum_name TEXT,
                message TEXT
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

if __name__ == '__main__':
    init_db('main.db')
    init_second('forum.db')
