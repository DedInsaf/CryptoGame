import tkinter as tk
import sqlite3
import random
import time
import threading
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from tkinter import messagebox

# 🎨 Новый стиль
BG_COLOR = "#222222"  # Тёмный фон
TEXT_COLOR = "#FFFFFF"  # Белый текст
BTN_COLOR = "#FF4500"  # Оранжево-красные кнопки
BTN_HOVER = "#CC3700"  # Тёмный оттенок при наведении
BTN_TEXT_COLOR = "#222222"  # Тёмный текст кнопок
GRAPH_COLOR = "yellow"  # Цвет графика

conn = sqlite3.connect("users.db", check_same_thread=False, timeout=20)
cursor = conn.cursor()

active_crypto_screen = None  # Хранит текущий экран торговли

def create_styled_button(parent, text, command):
    """Создает стилизованную кнопку."""
    btn = tk.Button(parent, text=text, command=command, font=("Arial", 12, "bold"),
                    fg=BTN_TEXT_COLOR, bg=BTN_COLOR, activebackground=BTN_HOVER,
                    relief="flat", bd=2, padx=10, pady=5, cursor="hand2")
    btn.pack(pady=5, fill="x")
    return btn

def show_trading_screen(user_id, crypto, root_frame, show_main_screen):
    """Показывает экран торговли криптовалютой с интерактивным графиком"""
    global active_crypto_screen
    active_crypto_screen = crypto

    # Очистка предыдущих виджетов
    for widget in root_frame.winfo_children():
        widget.destroy()

    # Настройка основного фрейма
    root_frame.configure(bg=BG_COLOR)
    header = tk.Label(root_frame, text=f"{crypto} - Торговля",
                      font=("Arial", 16, "bold"), fg=TEXT_COLOR, bg=BG_COLOR)
    header.pack(pady=10)

    # Контейнер для графика
    graph_frame = tk.Frame(root_frame, bg=BG_COLOR)
    graph_frame.pack(fill="both", expand=True, padx=20, pady=10)

    # Инициализация графика
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.set_facecolor(BG_COLOR)
    fig.patch.set_facecolor(BG_COLOR)
    canvas = FigureCanvasTkAgg(fig, master=graph_frame)
    canvas.get_tk_widget().pack(fill="both", expand=True)

    # Элементы управления
    price_label = tk.Label(root_frame, text="Текущая цена: ...",
                           font=("Arial", 14), fg=TEXT_COLOR, bg=BG_COLOR)
    price_label.pack(pady=5)

    # Переменные для управления графиком
    press_pos = None
    xlim_start = None
    ylim_start = None
    ZOOM_FACTOR = 1.2

    # Обработчики событий мыши
    def on_press(event):
        nonlocal press_pos, xlim_start, ylim_start
        if event.button == 1:  # ЛКМ
            press_pos = (event.x, event.y)
            xlim_start = ax.get_xlim()
            ylim_start = ax.get_ylim()

    def on_motion(event):
        nonlocal press_pos, xlim_start
        if press_pos is None or event.xdata is None:
            return

        dx = (event.x - press_pos[0]) * 0.5  # Чувствительность перемещения
        ax.set_xlim(xlim_start[0] - dx, xlim_start[1] - dx)
        canvas.draw_idle()

    def on_release(event):
        nonlocal press_pos
        press_pos = None

    def on_scroll(event):
        nonlocal xlim_start, ylim_start
        cur_xlim = ax.get_xlim()
        cur_ylim = ax.get_ylim()

        xdata = event.xdata or (cur_xlim[0] + cur_xlim[1]) / 2
        ydata = event.ydata or (cur_ylim[0] + cur_ylim[1]) / 2

        if event.button == 'up':
            scale_factor = 1 / ZOOM_FACTOR
        elif event.button == 'down':
            scale_factor = ZOOM_FACTOR
        else:
            return

        ax.set_xlim([
            xdata - (xdata - cur_xlim[0]) * scale_factor,
            xdata + (cur_xlim[1] - xdata) * scale_factor
        ])
        ax.set_ylim([
            ydata - (ydata - cur_ylim[0]) * scale_factor,
            ydata + (cur_ylim[1] - ydata) * scale_factor
        ])
        canvas.draw_idle()

    # Привязка событий
    canvas.mpl_connect("button_press_event", on_press)
    canvas.mpl_connect("motion_notify_event", on_motion)
    canvas.mpl_connect("button_release_event", on_release)
    canvas.mpl_connect("scroll_event", on_scroll)

    # Кнопка сброса масштаба
    def reset_zoom():
        ax.relim()
        ax.autoscale_view()
        canvas.draw()

    btn_reset = tk.Button(root_frame, text="Сбросить масштаб", command=reset_zoom,
                          font=("Arial", 10), bg=BTN_COLOR, fg=BTN_TEXT_COLOR)
    btn_reset.pack(pady=5)

    # Поле ввода количества
    amount_frame = tk.Frame(root_frame, bg=BG_COLOR)
    amount_frame.pack(pady=10)

    tk.Label(amount_frame, text="Количество:", font=("Arial", 12),
             fg=TEXT_COLOR, bg=BG_COLOR).pack(side="left")

    amount_var = tk.DoubleVar(value=1.0)
    amount_entry = tk.Entry(amount_frame, textvariable=amount_var,
                            font=("Arial", 12), width=10, bg="#333333",
                            fg=TEXT_COLOR, insertbackground=TEXT_COLOR)
    amount_entry.pack(side="left", padx=5)

    # Кнопки действий
    btn_frame = tk.Frame(root_frame, bg=BG_COLOR)
    btn_frame.pack(pady=10)

    create_styled_button(btn_frame, "Купить",
                         lambda: buy_crypto(user_id, crypto, amount_var.get()))
    create_styled_button(btn_frame, "Продать",
                         lambda: show_sell_window(user_id, crypto))
    create_styled_button(btn_frame, "Назад",
                         lambda: stop_trading_and_go_back(user_id, root_frame, show_main_screen))

    # Функция обновления графика
    def update_graph():
        """Обновляет график и цену, сохраняя позицию просмотра"""
        if active_crypto_screen != crypto or not root_frame.winfo_exists():
            return

        try:
            # Атомарно получаем текущую цену и историю
            conn = sqlite3.connect("users.db")
            cursor = conn.cursor()

            # Получаем данные в одной транзакции
            cursor.execute("BEGIN TRANSACTION")
            cursor.execute("SELECT price FROM crypto_prices WHERE crypto=?", (crypto,))
            current_price = cursor.fetchone()[0]

            cursor.execute("""
                SELECT price 
                FROM price_history 
                WHERE crypto=? 
                ORDER BY timestamp ASC
                LIMIT 100
            """, (crypto,))
            price_history = [p[0] for p in cursor.fetchall()]
            conn.commit()

            if len(price_history) < 1:
                return

            # Сохраняем текущие границы ДО обновления графика
            current_xlim = ax.get_xlim()
            current_ylim = ax.get_ylim()

            # Исправление ошибки сравнения массивов
            user_modified = not np.allclose(current_xlim, ax.dataLim.intervalx)

            # Обновление данных
            ax.clear()
            x_values = list(range(len(price_history)))

            ax.plot(
                x_values,
                price_history,
                marker='o',
                markersize=3,
                linestyle='-',
                color=GRAPH_COLOR,
                linewidth=1.5
            )

            ax.set_ylim(bottom=0)

            # Настройки графика
            ax.set_title(f'{crypto} - ${current_price:.2f}', color=TEXT_COLOR, pad=10)
            ax.set_xlabel('Временные точки', color=TEXT_COLOR)
            ax.grid(color="#444444")
            ax.tick_params(colors=TEXT_COLOR)

            # Восстановление позиции
            if not user_modified:
                if len(price_history) > 20:
                    ax.set_xlim(len(price_history) - 20, len(price_history) + 2)
                ax.autoscale(axis='y')
                ax.set_ylim(bottom=0)
            else:
                ax.set_xlim(current_xlim)
                ax.set_ylim(current_ylim)

            canvas.draw()
            price_label.config(text=f'Текущая цена: {current_price:.2f} $')

        except Exception as e:
            print(f"Ошибка обновления: {str(e)}")
            conn.rollback()

        finally:
            conn.close()
            root_frame.after(2000, update_graph)

    # Первый запуск обновления
    update_graph()

def stop_trading_and_go_back(user_id, root_frame, show_main_screen):
    """Останавливает обновление и возвращает пользователя в главное меню"""
    global active_crypto_screen
    active_crypto_screen = None
    show_main_screen(user_id)

def buy_crypto(user_id, crypto, amount):
    global conn
    """Покупает криптовалюту по текущей цене"""
    try:
        # Получаем актуальную цену из базы данных
        cursor.execute("SELECT price FROM crypto_prices WHERE crypto=?", (crypto,))
        price = cursor.fetchone()[0]

        # Рассчитываем общую стоимость покупки
        total_price = price * amount

        # Проверяем баланс пользователя
        cursor.execute("SELECT balance FROM users WHERE id=?", (user_id,))
        balance = cursor.fetchone()[0]

        if balance >= total_price:
            # Обновляем баланс пользователя
            cursor.execute("UPDATE users SET balance = balance - ? WHERE id = ?", (total_price, user_id))

            # Обновляем портфель пользователя
            cursor.execute("""
                INSERT INTO portfolio (user_id, crypto, amount)
                VALUES (?, ?, ?)
                ON CONFLICT(user_id, crypto) DO UPDATE SET amount = amount + ?
            """, (user_id, crypto, amount, amount))

            # Сохраняем изменения в базе данных
            conn.commit()

            show_non_blocking_info(f"Вы купили {amount:.2f} {crypto} за {total_price:.2f} $")
        else:
            messagebox.showwarning("Ошибка", "Недостаточно средств!")
    except Exception as e:
        print(f"Ошибка при покупке: {str(e)}")
        conn.rollback()

def show_sell_window(user_id, crypto):
    """Показывает окно продажи"""
    sell_window = tk.Toplevel()
    sell_window.title(f"Продажа {crypto}")
    sell_window.geometry("300x150")
    sell_window.configure(bg=BG_COLOR)

    cursor.execute("SELECT amount FROM portfolio WHERE user_id=? AND crypto=?", (user_id, crypto))
    result = cursor.fetchone()
    max_amount = result[0] if result else 0

    tk.Label(sell_window, text=f"Продажа {crypto}", font=("Arial", 12), fg=TEXT_COLOR, bg=BG_COLOR).pack()

    amount_var = tk.DoubleVar(value=max_amount if max_amount > 0 else 0.1)

    amount_slider = tk.Scale(sell_window, from_=0.1, to=max_amount, resolution=0.1, orient="horizontal", variable=amount_var,
                              bg=BG_COLOR, fg=TEXT_COLOR, highlightbackground=BG_COLOR)
    amount_slider.pack()

    create_styled_button(sell_window, "Продать", lambda: confirm_sell(user_id, crypto, amount_var.get(), sell_window))

def confirm_sell(user_id, crypto, amount, sell_window):
    """Завершает продажу"""
    sell_crypto(user_id, crypto, amount)
    sell_window.destroy()


def sell_crypto(user_id, crypto, amount):
    """Продает криптовалюту по текущей цене"""
    cursor.execute("SELECT price FROM crypto_prices WHERE crypto=?", (crypto,))
    price = cursor.fetchone()[0]
    total_price = price * amount

    cursor.execute("SELECT amount FROM portfolio WHERE user_id=? AND crypto=?", (user_id, crypto))
    result = cursor.fetchone()

    if result and result[0] >= amount:
        cursor.execute("UPDATE users SET balance = balance + ? WHERE id = ?", (total_price, user_id))
        cursor.execute("UPDATE portfolio SET amount = amount - ? WHERE user_id = ? AND crypto = ?",
                       (amount, user_id, crypto))
        conn.commit()
        show_non_blocking_info(f"Вы продали {amount:.2f} {crypto} за {total_price:.2f} $")
    else:
        messagebox.showwarning("Ошибка", "Недостаточно криптовалюты для продажи!")


def update_prices():
    """Обновляет цены атомарно"""
    global conn  # Используем глобальное соединение

    while True:
        try:
            cursor = conn.cursor()
            cursor.execute("BEGIN IMMEDIATE")  # Явное начало транзакции

            for crypto in ["Bitcoin", "Ethereum", "Dogecoin"]:
                cursor.execute("SELECT price FROM crypto_prices WHERE crypto=?", (crypto,))
                old_price = cursor.fetchone()[0]

                new_price = max(1, old_price + random.uniform(-5, 5))

                cursor.execute("UPDATE crypto_prices SET price=? WHERE crypto=?", (new_price, crypto))
                cursor.execute("INSERT INTO price_history (crypto, price) VALUES (?, ?)", (crypto, new_price))

            conn.commit()  # Фиксация изменений

        except sqlite3.OperationalError as e:
            print(f"Ошибка: {str(e)}. Повторная попытка...")
            conn.rollback()
            time.sleep(1)

        finally:
            time.sleep(2)  # Интервал между обновлениями


def start_price_thread():
    """Запускает поток обновления цен."""
    global conn
    conn = sqlite3.connect("users.db", check_same_thread=False, timeout=20)

    thread = threading.Thread(target=update_prices, daemon=True)
    thread.start()

def show_non_blocking_info(message):
    top = tk.Toplevel()
    top.title("Уведомление")
    tk.Label(top, text=message).pack(padx=20, pady=10)
    tk.Button(top, text="OK", command=top.destroy).pack(pady=5)