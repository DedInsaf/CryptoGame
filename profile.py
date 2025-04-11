import tkinter as tk
import sqlite3

# 🎨 Новый стиль
BG_COLOR = "#222222"   # Тёмный фон
TEXT_COLOR = "#FFFFFF"  # Белый текст
BTN_COLOR = "#FF4500"   # Оранжево-красные кнопки
BTN_HOVER = "#CC3700"   # Тёмный оттенок при наведении
BTN_TEXT_COLOR = "#222222"  # Тёмный текст кнопок

conn = sqlite3.connect("users.db", check_same_thread=False)
cursor = conn.cursor()

def show_profile_screen(user_id, root_frame, show_main_screen):
    """Экран профиля с исправлением ошибки"""
    for widget in root_frame.winfo_children():
        widget.destroy()

    root_frame.configure(bg=BG_COLOR)

    tk.Label(root_frame, text="Профиль", font=("Arial", 16, "bold"), fg=TEXT_COLOR, bg=BG_COLOR).pack()

    balance_label = tk.Label(root_frame, text="Баланс: ...", font=("Arial", 14), fg=TEXT_COLOR, bg=BG_COLOR)
    balance_label.pack()

    portfolio_label = tk.Label(root_frame, text="Криптовалюта:", font=("Arial", 14), fg=TEXT_COLOR, bg=BG_COLOR)
    portfolio_label.pack()

    updating = True  # Флаг, контролирующий обновление

    def update_profile():
        """Обновляет баланс и крипту"""
        if not updating:  # Проверяем, нужно ли обновлять данные
            return

        if balance_label.winfo_exists():  # Проверяем, существует ли виджет перед обновлением
            cursor.execute("SELECT balance FROM users WHERE id=?", (user_id,))
            balance = cursor.fetchone()[0]
            balance_label.config(text=f"Баланс: {balance:.2f} $")

            cursor.execute("SELECT crypto, amount FROM portfolio WHERE user_id=?", (user_id,))
            portfolio = cursor.fetchall()

            portfolio_text = "Криптовалюта:\n"
            for crypto, amount in portfolio:
                portfolio_text += f"{crypto}: {amount} шт.\n"

            portfolio_label.config(text=portfolio_text)
            root_frame.after(3000, update_profile)

    update_profile()

    def go_back():
        nonlocal updating
        updating = False  # Останавливаем обновление при выходе
        show_main_screen(user_id)

    btn_back = tk.Button(root_frame, text="Назад", command=go_back, font=("Arial", 12, "bold"),
                         fg=BTN_TEXT_COLOR, bg=BTN_COLOR, activebackground=BTN_HOVER,
                         relief="flat", bd=2, padx=10, pady=5, cursor="hand2")
    btn_back.pack(pady=10, fill="x")