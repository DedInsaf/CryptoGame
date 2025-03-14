import sys
import requests
from PyQt6.QtWidgets import (
    QApplication,
    QWidget,
    QLabel,
    QLineEdit,
    QPushButton,
    QComboBox,
    QVBoxLayout,
    QMessageBox
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont

API_BASE_URL = "http://localhost:8000/api"


class CryptoApp(QWidget):
    def __init__(self):
        super().__init__()
        self.user_id = None
        self.current_balance = 0.0
        self.initUI()
        self.update_prices()

        # Таймер для обновления цен каждые 5 секунд
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_prices)
        self.timer.start(5000)

    def initUI(self):
        self.setWindowTitle("KidsCrypto Exchange")
        self.setGeometry(300, 300, 400, 300)
        self.setStyleSheet("background-color: #f0f0f0;")

        layout = QVBoxLayout()

        # Регистрация
        self.register_section(layout)

        # Отображение баланса
        self.balance_label = QLabel("Balance: 0 KID")
        self.balance_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        self.balance_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.balance_label)

        # Выбор криптовалюты
        self.crypto_combo = QComboBox()
        self.crypto_combo.addItems(["KidCoin", "EduToken", "CryptoStar"])
        self.crypto_combo.setFont(QFont("Arial", 12))
        layout.addWidget(self.crypto_combo)

        # Поле для ввода количества
        self.amount_input = QLineEdit()
        self.amount_input.setPlaceholderText("Amount to buy")
        self.amount_input.setFont(QFont("Arial", 12))
        layout.addWidget(self.amount_input)

        # Кнопка покупки
        self.buy_button = QPushButton("Buy")
        self.buy_button.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        self.buy_button.setStyleSheet(
            "background-color: #4CAF50; color: white; padding: 10px;"
        )
        self.buy_button.clicked.connect(self.buy_crypto)
        layout.addWidget(self.buy_button)

        # Статус
        self.status_label = QLabel("")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.status_label)

        self.setLayout(layout)

    def register_section(self, layout):
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Username")
        layout.addWidget(self.username_input)

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Password")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(self.password_input)

        register_btn = QPushButton("Register")
        register_btn.clicked.connect(self.register_user)
        layout.addWidget(register_btn)

    def register_user(self):
        username = self.username_input.text()
        password = self.password_input.text()

        try:
            response = requests.post(
                f"{API_BASE_URL}/auth/register",
                json={"username": username, "password": password}
            )
            data = response.json()
            self.user_id = data["user_id"]
            self.current_balance = 1000.0
            self.update_balance_display()
            QMessageBox.information(self, "Success", "Registration successful!")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def update_prices(self):
        try:
            response = requests.get(f"{API_BASE_URL}/crypto/prices")
            self.prices = response.json()
        except:
            self.status_label.setText("Error fetching prices")

    def buy_crypto(self):
        if not self.user_id:
            QMessageBox.warning(self, "Error", "Please register first!")
            return

        crypto = self.crypto_combo.currentText()
        amount = self.amount_input.text()

        try:
            amount = float(amount)
            if amount <= 0:
                raise ValueError
        except:
            QMessageBox.warning(self, "Error", "Invalid amount")
            return

        try:
            response = requests.post(
                f"{API_BASE_URL}/crypto/buy",
                json={
                    "user_id": self.user_id,
                    "crypto_name": crypto,
                    "amount": amount
                }
            )
            data = response.json()
            self.current_balance = data["new_balance"]
            self.update_balance_display()
            self.status_label.setText(data["message"])
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def update_balance_display(self):
        self.balance_label.setText(f"Balance: {self.current_balance:.2f} KID")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CryptoApp()
    window.show()
    sys.exit(app.exec())