import sqlite3

def initialize_db():
    """Создает базу данных и таблицы, если их нет."""
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()

    # Таблица пользователей
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            balance REAL DEFAULT 1000
        )
    """)

    # Таблица портфеля пользователя
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS portfolio (
            user_id INTEGER,
            crypto TEXT,
            amount REAL DEFAULT 0,
            PRIMARY KEY(user_id, crypto),
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    """)

    # Таблица цен криптовалют
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS crypto_prices (
            crypto TEXT PRIMARY KEY,
            price REAL NOT NULL
        )
    """)

    # Таблица истории цен
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS price_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            crypto TEXT NOT NULL,
            price REAL NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Начальные данные о ценах криптовалют
    cursor.execute("INSERT OR IGNORE INTO crypto_prices (crypto, price) VALUES ('Bitcoin', 30000)")
    cursor.execute("INSERT OR IGNORE INTO crypto_prices (crypto, price) VALUES ('Ethereum', 2000)")
    cursor.execute("INSERT OR IGNORE INTO crypto_prices (crypto, price) VALUES ('Dogecoin', 0.1)")

    conn.commit()
    conn.close()

initialize_db()