import tkinter as tk
from auth import register_user, login_user
from trading import show_trading_screen, start_price_thread
from profile import show_profile_screen, BTN_TEXT_COLOR
from db import initialize_db

# 🎨 Настройки стиля
BG_COLOR = "#222222"
FG_COLOR = "white"
BTN_COLOR = "#444444"
BTN_HOVER = "#666666"

initialize_db()

root = tk.Tk()
root.title("Криптобиржа для детей")
root.geometry("1920x1080")
root.attributes("-fullscreen", True)
root.configure(bg=BG_COLOR)

root_frame = tk.Frame(root, bg=BG_COLOR)
root_frame.pack(fill="both", expand=True)

def create_styled_button(parent, text, command):
    """Создает стилизованную кнопку."""
    btn = tk.Button(parent, text=text, command=command, font=("Arial", 12, "bold"),
                    fg=BTN_TEXT_COLOR, bg=BTN_COLOR, activebackground=BTN_HOVER,
                    relief="flat", bd=2, padx=10, pady=5, cursor="hand2")
    btn.pack(pady=5)
    return btn

def show_login_screen():
    """Экран входа"""
    for widget in root_frame.winfo_children():
        widget.destroy()

    tk.Label(root_frame, text="Вход", font=("Arial", 16, "bold"), fg=FG_COLOR, bg=BG_COLOR).pack()

    tk.Label(root_frame, text="Email:", font=("Arial", 12), fg=FG_COLOR, bg=BG_COLOR).pack()
    email_entry = tk.Entry(root_frame, font=("Arial", 12), bg="#333333", fg=FG_COLOR)
    email_entry.pack()

    tk.Label(root_frame, text="Пароль:", font=("Arial", 12), fg=FG_COLOR, bg=BG_COLOR).pack()
    password_entry = tk.Entry(root_frame, show="*", font=("Arial", 12), bg="#333333", fg=FG_COLOR)
    password_entry.pack()

    def login():
        user_id = login_user(email_entry.get(), password_entry.get())
        if user_id:
            show_main_screen(user_id)

    create_styled_button(root_frame, "Войти", login)
    create_styled_button(root_frame, "Регистрация", show_register_screen)

def show_register_screen():
    """Экран регистрации"""
    for widget in root_frame.winfo_children():
        widget.destroy()

    tk.Label(root_frame, text="Регистрация", font=("Arial", 16, "bold"), fg=FG_COLOR, bg=BG_COLOR).pack()

    tk.Label(root_frame, text="Имя:", font=("Arial", 12), fg=FG_COLOR, bg=BG_COLOR).pack()
    name_entry = tk.Entry(root_frame, font=("Arial", 12), bg="#333333", fg=FG_COLOR)
    name_entry.pack()

    tk.Label(root_frame, text="Email:", font=("Arial", 12), fg=FG_COLOR, bg=BG_COLOR).pack()
    email_entry = tk.Entry(root_frame, font=("Arial", 12), bg="#333333", fg=FG_COLOR)
    email_entry.pack()

    tk.Label(root_frame, text="Пароль:", font=("Arial", 12), fg=FG_COLOR, bg=BG_COLOR).pack()
    password_entry = tk.Entry(root_frame, show="*", font=("Arial", 12), bg="#333333", fg=FG_COLOR)
    password_entry.pack()

    def register():
        user_id = register_user(name_entry.get(), email_entry.get(), password_entry.get())
        if user_id:
            show_main_screen(user_id)

    create_styled_button(root_frame, "Зарегистрироваться", register)
    create_styled_button(root_frame, "Назад", show_login_screen)

def show_main_screen(user_id):
    """Главное меню"""
    for widget in root_frame.winfo_children():
        widget.destroy()

    tk.Label(root_frame, text="Главное меню", font=("Arial", 16, "bold"), fg=FG_COLOR, bg=BG_COLOR).pack()

    create_styled_button(root_frame, "Профиль", lambda: show_profile_screen(user_id, root_frame, show_main_screen))

    for crypto in ["Bitcoin", "Ethereum", "Dogecoin"]:
        create_styled_button(root_frame, crypto, lambda c=crypto: show_trading_screen(user_id, c, root_frame, show_main_screen))

# Запускаем начальный экран
show_login_screen()

start_price_thread()
root.mainloop()