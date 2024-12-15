import sys
import psycopg2
import os
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QStackedWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLabel,
    QLineEdit,
    QMessageBox,
    QListWidget,
    QListWidgetItem
)
from PyQt5.QtGui import QIcon
from datetime import datetime

# Загружаем переменные окружения из .env файла
load_dotenv()

# Конфигурация базы данных из .env файла
DB_CONFIG = {
    'dbname': os.getenv('DB_NAME'),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'host': os.getenv('DB_HOST'),
    'port': os.getenv('DB_PORT')
}
# Функция для добавления компонентов в базу данных
def add_component_to_db(category, name, price, description):
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()

        query = """
            INSERT INTO Компоненты (Категория, Название, Цена, Описание)
            VALUES (%s, %s, %s, %s)
        """
        cursor.execute(query, (category, name, price, description))
        conn.commit()

        cursor.close()
        conn.close()
        print(f"{category} '{name}' добавлен в базу данных.")
    except Exception as e:
        print(f"Ошибка добавления компонента: {e}")

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Информационная система для сборки ПК")
        self.setGeometry(100, 100, 800, 600)

        # Инициализация переменной для хранения общей стоимости сборки
        self.total_price = 0

        # Словарь для отслеживания выбранных компонентов и их цен
        self.selected_components = {}

        # Подключение к базе данных через объект Database
        self.db = Database()  # Здесь создаём экземпляр класса Database
        self.cursor = self.db.cursor

        # Основной стек виджетов
        self.central_widget = QStackedWidget()
        self.setCentralWidget(self.central_widget)

        # Экран профиля
        self.profile_screen = self.create_profile_screen()
        self.central_widget.addWidget(self.profile_screen)

        # Главный экран
        self.main_menu = self.create_main_menu()
        self.central_widget.addWidget(self.main_menu)

        # Экран новой сборки
        self.new_build_screen = self.create_new_build_screen()
        self.central_widget.addWidget(self.new_build_screen)

        # Экран склада комплектующих
        self.components_screen = self.create_components_screen()
        self.central_widget.addWidget(self.components_screen)

        # Экран активных сборок
        self.active_builds_screen = self.create_active_builds_screen()
        self.central_widget.addWidget(self.active_builds_screen)

        # Сначала показываем главный экран, а не экран профиля
        self.central_widget.setCurrentWidget(self.main_menu)

    def create_profile_screen(self):
        """Создание экрана профиля"""
        screen = QWidget()
        layout = QVBoxLayout()

        self.profile_info_label = QLabel("Никнейм: null\nДата регистрации: --/--/----")
        layout.addWidget(self.profile_info_label)

        logout_button = QPushButton("Выход")
        logout_button.clicked.connect(self.logout)
        layout.addWidget(logout_button)

        screen.setLayout(layout)
        return screen

    def logout(self):
        self.profile_info_label.setText("Никнейм: null\nДата регистрации: --/--/----")
        QMessageBox.information(self, "Выход", "Вы успешно вышли из профиля.")
        self.show_main_menu_screen()

    def show_main_menu_screen(self):
        self.central_widget.setCurrentWidget(self.main_menu)

    def register_user(self):
        username = self.registration_username_input.text()
        password = self.registration_password_input.text()

        if not username or not password:
            QMessageBox.warning(self, "Ошибка", "Все поля должны быть заполнены!")
            return

        try:
            self.db.execute_query(
                "INSERT INTO users (username, password) VALUES (%s, %s)",
                (username, password)
            )
            QMessageBox.information(self, "Успех", "Регистрация успешна!")
            self.show_profile_screen()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", "Ошибка регистрации: пользователь уже существует!")

    def show_profile_screen(self):
        self.central_widget.setCurrentWidget(self.profile_screen)

    def create_main_menu(self):
        """Создание главного меню"""
        screen = QWidget()
        layout = QVBoxLayout()

        # Кнопки
        buttons_layout = QVBoxLayout()
        btn_new_build = QPushButton("Новая сборка")
        btn_new_build.clicked.connect(lambda: self.central_widget.setCurrentWidget(self.new_build_screen))
        btn_components = QPushButton("Склад комплектующих")
        btn_components.clicked.connect(lambda: self.central_widget.setCurrentWidget(self.components_screen))
        btn_active_builds = QPushButton("Активные сборки")
        btn_active_builds.clicked.connect(lambda: self.central_widget.setCurrentWidget(self.active_builds_screen))
        btn_finished_builds = QPushButton("Завершённые сборки")

        for btn in [btn_new_build, btn_components, btn_active_builds, btn_finished_builds]:
            btn.setFixedHeight(50)
            buttons_layout.addWidget(btn)

        layout.addLayout(buttons_layout)
        screen.setLayout(layout)
        return screen

    def create_new_build_screen(self):
        """Создание экрана новой сборки"""
        screen = QWidget()
        layout = QVBoxLayout()

        # Верхняя панель
        top_bar = QHBoxLayout()
        back_btn = QPushButton("Назад")
        back_btn.setFixedSize(60, 40)
        back_btn.clicked.connect(lambda: self.central_widget.setCurrentWidget(self.main_menu))

        title_label = QLabel("Новая сборка")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        save_btn = QPushButton("Сохранить")
        delete_btn = QPushButton("Удалить")
        profile_btn = QPushButton("Профиль")
        profile_btn.setFixedSize(100, 40)
        profile_btn.clicked.connect(self.show_profile_screen)  # Добавлен обработчик для кнопки Профиль

        top_bar.addWidget(back_btn)
        top_bar.addWidget(title_label)
        top_bar.addStretch()
        top_bar.addWidget(delete_btn)
        top_bar.addWidget(save_btn)
        top_bar.addWidget(profile_btn)

        # Секция выбора комплектующих
        components_layout = QHBoxLayout()
        self.component_buttons = {}  # Словарь для хранения кнопок

        components = [
            ("Видеокарта", "Видеокарта"),
            ("Процессор", "Процессор"),
            ("Мат. плата", "Материнская плата"),
            ("Корпус", "Корпус"),
            ("Охлаждение процессора", "Охлаждение процессора"),
            ("Оперативная память", "Оперативная память"),
            ("Накопители", "Накопитель"),
            ("Блок питания", "Блок питания"),
            ("Доп. детали", "Доп. детали")
        ]

        for label, category in components:
            btn = QPushButton(label)
            btn.setFixedHeight(40)
            btn.clicked.connect(lambda checked, c=category: self.show_components_for_category(c))
            components_layout.addWidget(btn)
            self.component_buttons[category] = btn

        # Добавление элементов в основной макет
        layout.addLayout(top_bar)
        layout.addLayout(components_layout)

        # Список компонентов для новой сборки
        self.new_build_list = QListWidget()
        self.new_build_list.itemDoubleClicked.connect(self.select_component)  # Обработчик двойного клика
        layout.addWidget(self.new_build_list)

        # Метка для отображения цены сборки
        self.build_price_label = QLabel("Цена: 0 руб.")
        layout.addWidget(self.build_price_label)

        screen.setLayout(layout)
        return screen

    def select_component(self, item):
        try:
            lines = item.text().split('\n')
            selected_component = lines[0].split(': ')[1]
            component_price = float(lines[1].split(': ')[1].split(' ')[0])

            if self.current_category in self.selected_components:
                old_price = self.selected_components[self.current_category]
                self.total_price -= old_price

            self.selected_components[self.current_category] = component_price
            self.total_price += component_price

            self.update_build_price()

            # Обновляем текст кнопки
            if self.current_category in self.component_buttons:
                btn = self.component_buttons[self.current_category]
                btn.setText(f"{self.current_category}\n{selected_component}")

        except Exception as e:
            print(f"Ошибка при выборе компонента: {e}")

    def update_build_price(self):
        """Обновление общей цены сборки"""
        self.build_price_label.setText(f"Цена: {self.total_price} руб.")

    def show_components_for_category(self, category):
        """Отображение компонентов для выбранной категории"""
        self.current_category = category
        try:
            if self.db.conn.closed:
                # Повторное подключение к БД в случае разрыва
                self.db = Database()
                self.cursor = self.db.cursor

            self.cursor.execute("SELECT Категория, Название, Цена, Описание FROM Компоненты WHERE Категория = %s", (category,))
            components = self.cursor.fetchall()
            self.new_build_list.clear()  # Очищаем список перед добавлением новых элементов

            if not components:
                self.new_build_list.addItem(QListWidgetItem("Нет компонентов в этой категории."))
                return

            for category, name, price, description in components:
                item_text = f"{category}: {name}\nЦена: {price} руб.\nОписание: {description}"
                self.new_build_list.addItem(QListWidgetItem(item_text))
        except Exception as e:
            print(f"Ошибка при загрузке компонентов: {e}")

    def create_components_screen(self):
        """Создание экрана склада комплектующих"""
        screen = QWidget()
        layout = QVBoxLayout()

        self.components_list = QListWidget()
        self.load_and_display_all_components()
        layout.addWidget(self.components_list)

        screen.setLayout(layout)
        return screen

    def load_and_display_all_components(self):
        """Загрузка всех компонентов для отображения"""
        try:
            self.cursor.execute("SELECT Категория, Название, Цена FROM Компоненты")
            components = self.cursor.fetchall()

            self.components_list.clear()
            for component in components:
                item_text = f"{component[0]}: {component[1]}\nЦена: {component[2]} руб."
                item = QListWidgetItem(item_text)
                self.components_list.addItem(item)
        except Exception as e:
            print(f"Ошибка при загрузке компонентов: {e}")

    def create_active_builds_screen(self):
        """Создание экрана активных сборок"""
        screen = QWidget()
        layout = QVBoxLayout()

        self.active_builds_list = QListWidget()
        layout.addWidget(self.active_builds_list)

        screen.setLayout(layout)
        return screen


class Database:
    def __init__(self):
        try:
            self.conn = psycopg2.connect(**DB_CONFIG)
            self.cursor = self.conn.cursor()
            print("Подключение к базе данных успешно!")
        except psycopg2.OperationalError as e:
            print(f"Ошибка подключения к базе данных: {e}")
            sys.exit(1)

    def execute_query(self, query, params=None):
        try:
            self.cursor.execute(query, params)
            self.conn.commit()
        except Exception as e:
            print("Ошибка выполнения запроса:", e)
            self.conn.rollback()

    def fetchone(self):
        return self.cursor.fetchone()

    def fetchall(self):
        return self.cursor.fetchall()

    def close(self):
        self.cursor.close()
        self.conn.close()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
