import sys
import psycopg2
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QStackedWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLabel,
    QListWidget,
    QListWidgetItem
)
from PyQt5.QtGui import QIcon
from decimal import Decimal

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Информационная система для сборки ПК")
        self.setGeometry(100, 100, 800, 600)

        # Подключение к базе данных
        self.db_connection = self.connect_to_db()
        self.cursor = self.db_connection.cursor()

        # Основной стек виджетов
        self.central_widget = QStackedWidget()
        self.setCentralWidget(self.central_widget)

        # Главный экран
        self.main_menu = self.create_main_menu()
        self.central_widget.addWidget(self.main_menu)

        # Экран новой сборки
        self.new_build_screen = self.create_new_build_screen()
        self.central_widget.addWidget(self.new_build_screen)

        # Экран склада комплектующих
        self.components_screen = self.create_components_screen()
        self.central_widget.addWidget(self.components_screen)

    def connect_to_db(self):
        try:
            # Подключение к базе данных
            conn = psycopg2.connect(
                dbname="ИС",  # Имя базы данных
                user="postgres",  # Имя пользователя
                password="35900956",  # Пароль пользоват
                host="localhost",  # Хост, обычно "localhost"
                port="5432"  # Порт по умолчанию для PostgreSQL
            )
            print("Подключение к базе данных успешно!")
            return conn
        except Exception as e:
            print(f"Ошибка подключения к базе данных: {e}")
            return None

    def load_components(self, category=None):
        """Загрузка компонентов из базы данных с фильтрацией по категории"""
        if category:
            query = "SELECT * FROM components WHERE category = %s"
            self.cursor.execute(query, (category,))
        else:
            query = "SELECT * FROM components"
            self.cursor.execute(query)

        components = self.cursor.fetchall()
        return components

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
        back_btn = QPushButton()
        back_btn.setIcon(QIcon("back_icon.png"))  # Замените на путь к иконке
        back_btn.setFixedSize(40, 40)
        back_btn.clicked.connect(lambda: self.central_widget.setCurrentWidget(self.main_menu))

        title_label = QLabel("Новая сборка")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        save_btn = QPushButton("Сохранить")
        delete_btn = QPushButton("Удалить")
        profile_btn = QPushButton()
        profile_btn.setIcon(QIcon("user_icon.png"))  # Замените на путь к иконке
        profile_btn.setFixedSize(50, 50)

        top_bar.addWidget(back_btn)
        top_bar.addWidget(title_label)
        top_bar.addStretch()
        top_bar.addWidget(delete_btn)
        top_bar.addWidget(save_btn)
        top_bar.addWidget(profile_btn)

        # Секция выбора комплектующих
        components_layout = QHBoxLayout()
        components = [
            ("Видеокарта", "Видеокарты"),
            ("Процессор", "Процессоры"),
            ("Мат. плата", "Мат. платы"),
            ("Корпус", "Корпуса"),
            ("Охлаждение процессора", "Охлаждения процессора"),
            ("Оперативная память", "Оперативная память"),
            ("Накопители", "Накопители"),
            ("Блок питания", "Блок питания"),
            ("Доп. детали", "Доп. детали")
        ]
        for label, category in components:
            btn = QPushButton(label)
            btn.setFixedHeight(40)
            btn.clicked.connect(lambda checked, c=category: self.show_components_for_category(c))
            components_layout.addWidget(btn)

        # Добавление элементов в основной макет
        layout.addLayout(top_bar)
        layout.addLayout(components_layout)

        # Список компонентов для новой сборки
        self.new_build_list = QListWidget()
        layout.addWidget(self.new_build_list)

        screen.setLayout(layout)
        return screen

    def show_components_for_category(self, category):
        """Отображение компонентов для выбранной категории на вкладке 'Новая сборка'"""
        self.cursor.execute("SELECT * FROM components WHERE category = %s", (category,))
        components = self.cursor.fetchall()

        # Очищаем старый список компонентов
        self.new_build_list.clear()

        for component in components:
            item = QListWidgetItem(f"{component[1]}\nЦена: {component[4]} руб.\nОписание: {component[3]}")
            self.new_build_list.addItem(item)

    def create_components_screen(self):
        """Создание экрана склада комплектующих"""
        screen = QWidget()
        layout = QVBoxLayout()

        # Список компонентов
        self.components_list = QListWidget()
        self.load_and_display_all_components()

        layout.addWidget(self.components_list)
        screen.setLayout(layout)
        return screen

    def load_and_display_all_components(self):
        """Загрузка и отображение всех компонентов на вкладке 'Склад комплектующих'"""
        components = self.load_components()
        for component in components:
            item = QListWidgetItem(f"{component[1]}\nЦена: {component[4]} руб.\nОписание: {component[3]}")
            self.components_list.addItem(item)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
