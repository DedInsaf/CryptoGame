import sqlite3
import hashlib

conn = sqlite3.connect("users.db", check_same_thread=False)
cursor = conn.cursor()

def hash_password(password):
    """Шифрование пароля"""
    return hashlib.sha256(password.encode()).hexdigest()

def register_user(name, email, password):
    """Регистрация нового пользователя"""
    hashed_password = hash_password(password)
    try:
        cursor.execute("INSERT INTO users (name, email, password) VALUES (?, ?, ?)", (name, email, hashed_password))
        conn.commit()
        return cursor.lastrowid
    except sqlite3.IntegrityError:
        return None  # Если email уже существует

def login_user(email, password):
    """Авторизация пользователя"""
    hashed_password = hash_password(password)
    cursor.execute("SELECT id FROM users WHERE email=? AND password=?", (email, hashed_password))
    user = cursor.fetchone()
    return user[0] if user else None