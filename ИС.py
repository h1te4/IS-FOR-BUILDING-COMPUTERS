import sys
import psycopg2
import bcrypt
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
        # Начальные значения никнейма и даты регистрации
        self.username = None
        self.registration_date = None

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
        screen = QWidget()
        layout = QVBoxLayout()

        # Верхняя панель с кнопкой "Назад"
        top_bar = QHBoxLayout()
        back_button = QPushButton("Назад")
        back_button.clicked.connect(self.show_main_menu_screen)  # Переход в главное меню
        top_bar.addWidget(back_button)

        top_bar.addStretch()  # Раздвигает элементы вправо, оставляя кнопку слева

        layout.addLayout(top_bar)  # Добавляем верхнюю панель в layout

        if self.is_user_logged_in():
            # Если пользователь авторизован
            self.profile_info_label = QLabel(f"Никнейм: {self.username}\nДата регистрации: {self.registration_date}")
            layout.addWidget(self.profile_info_label)

            # Кнопка выхода
            logout_button = QPushButton("Выход")
            logout_button.clicked.connect(self.logout)
            layout.addWidget(logout_button)
        else:
            # Если пользователь не авторизован
            self.profile_info_label = QLabel("Вы не вошли в профиль")
            layout.addWidget(self.profile_info_label)

            # Кнопка регистрации
            register_button = QPushButton("Регистрация")
            register_button.clicked.connect(self.open_registration_window)
            layout.addWidget(register_button)

            # Кнопка входа
            login_button = QPushButton("Вход")
            login_button.clicked.connect(self.open_login_window)
            layout.addWidget(login_button)

        screen.setLayout(layout)
        return screen

    # Проверка зарегистрирован ли пользователь
    def is_user_logged_in(self):
        return self.username is not None

    def get_user_id(self):
        if not self.is_user_logged_in():
            return None

        self.cursor.execute("SELECT id FROM Пользователи WHERE Никнейм = %s", (self.username,))
        result = self.cursor.fetchone()
        if result:
            return result[0]
        else:
            return None

    # Выход из профиля
    def logout(self):
        self.username = None
        self.registration_date = None
        self.refresh_profile_screen()

    # Обновление экрана профиля
    def refresh_profile_screen(self):
        self.profile_screen = self.create_profile_screen()
        self.central_widget.removeWidget(self.central_widget.widget(0))  # Удаляем старый профиль
        self.central_widget.insertWidget(0, self.profile_screen)  # Вставляем новый профиль
        self.central_widget.setCurrentWidget(self.profile_screen)  # Переключаемся на новый профиль

    # Открытие окна регистрации
    def open_registration_window(self):
        self.registration_window = AuthWindow(self, mode="register")
        self.registration_window.show()

    # Открытие окна входа
    def open_login_window(self):
        self.login_window = AuthWindow(self, mode="login")
        self.login_window.show()

    # Логин пользователя
    def login_user(self, username):
        self.username = username
        self.registration_date = self.get_registration_date(username)
        self.refresh_profile_screen()

    # Получение даты регистрации
    def get_registration_date(self, username):
        self.cursor.execute("SELECT Дата_регистрации FROM Пользователи WHERE Никнейм = %s", (username,))
        return self.cursor.fetchone()[0]

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

            # Хеш пароля
            hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

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
        btn_active_builds.clicked.connect(
            lambda: self.central_widget.setCurrentWidget(self.active_builds_screen))  # Исправлено

        btn_finished_builds = QPushButton("Завершённые сборки")
        btn_finished_builds.clicked.connect(lambda: self.central_widget.setCurrentWidget(self.finished_builds_screen))

        # Добавляем кнопки в макет
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
        save_btn.clicked.connect(self.save_build)  # Обработчик для кнопки "Сохранить"
        delete_btn = QPushButton("Удалить")
        delete_btn.clicked.connect(self.delete_build)  # Обработчик для кнопки "Удалить"
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
        # Нижняя панель с названием сборки
        bottom_bar = QHBoxLayout()
        new_build_label = QLabel("Новая сборка: ")  # Текст для названия сборки
        self.build_name_input = QLineEdit()  # Поле для ввода названия сборки
        self.build_name_input.setPlaceholderText("Введите название сборки...")
        bottom_bar.addWidget(new_build_label)
        bottom_bar.addWidget(self.build_name_input)

        layout.addLayout(bottom_bar)  # Добавляем нижнюю панель в layout

        screen.setLayout(layout)
        return screen

    def save_build(self):
        # Проверка, авторизован ли пользователь
        if not self.is_user_logged_in():
            QMessageBox.warning(self, "Ошибка", "Вы должны войти в профиль, чтобы сохранить сборку!")
            return

        build_name = self.build_name_input.text()

        # Проверка, чтобы название сборки не было пустым
        if not build_name.strip():
            QMessageBox.warning(self, "Ошибка", "Пожалуйста, введите название сборки!")
            return

        # Сохранение сборки в базу данных как активную
        try:
            # Вставляем сборку в таблицу "Сборки"
            self.cursor.execute(
                "INSERT INTO \"Сборки\" (\"Название_сборки\", \"Общая_цена\", \"id_пользователя\", \"Статус_сборки\") "
                "VALUES (%s, %s, %s, %s) RETURNING id",
                (build_name, self.total_price, self.get_user_id(), 'Активная')
            )
            build_id = self.cursor.fetchone()[0]  # Получаем ID только что вставленной сборки
            self.db.conn.commit()

            # Сохраняем компоненты для этой сборки в таблицу "Компоненты_сборки"
            for category, component_price in self.selected_components.items():
                # Для каждого выбранного компонента сохраняем его в таблице Компоненты_сборки
                self.cursor.execute(
                    "INSERT INTO \"Компоненты_сборки\" (\"id_сборки\", \"id_компонента\", \"Количество\") "
                    "VALUES (%s, (SELECT id FROM \"Компоненты\" WHERE \"Категория\" = %s LIMIT 1), %s)",
                    (build_id, category, 1)  # Пример: количество каждого компонента = 1
                )
            self.db.conn.commit()

            QMessageBox.information(self, "Успех", "Сборка успешно сохранена!")
        except Exception as e:
            self.db.conn.rollback()  # Если ошибка, откатываем изменения
            QMessageBox.critical(self, "Ошибка", f"Ошибка при сохранении сборки: {str(e)}")

    def delete_build(self, build_id):
        try:
            self.cursor.execute("DELETE FROM \"Сборки\" WHERE id = %s", (build_id,))
            self.db.conn.commit()
            QMessageBox.information(self, "Успех", "Сборка удалена.")
            self.show_active_builds()  # Перезагружаем список
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка при удалении сборки: {e}")

    def finish_build(self, build_id):
        try:
            self.cursor.execute("""
                UPDATE "Сборки" 
                SET Статус_сборки = 'Завершенная' 
                WHERE id = %s
            """, (build_id,))
            self.db.conn.commit()
            QMessageBox.information(self, "Успех", "Сборка перенесена в завершенные.")
            self.show_active_builds()  # Перезагружаем список
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка при завершении сборки: {e}")

    def edit_build(self, build_id):
        try:
            # Получаем текущие данные сборки
            self.cursor.execute("""
                SELECT Название_сборки, Общая_цена 
                FROM "Сборки" 
                WHERE id = %s
            """, (build_id,))
            build = self.cursor.fetchone()

            if build:
                build_name, total_price = build
                self.open_build_editor(build_id, build_name, total_price)
            else:
                QMessageBox.warning(self, "Ошибка", "Сборка не найдена.")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка при открытии сборки: {e}")

    def open_build_editor(self, build_id, build_name, total_price):
        editor_window = BuildEditor(self, build_id, build_name, total_price)
        editor_window.show()


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
        # Создание экрана активных сборок
        screen = QWidget()
        layout = QVBoxLayout()

        self.active_builds_list = QListWidget()
        layout.addWidget(self.active_builds_list)
        
        back_button = QPushButton("Назад")
        back_button.clicked.connect(self.show_main_menu_screen)
        layout.addWidget(back_button)

        # Вызов метода для отображения активных сборок
        self.show_active_builds()

        screen.setLayout(layout)
        return screen

    def show_active_builds(self):
        try:
            # Очищаем список перед обновлением
            self.active_builds_list.clear()

            # Получаем активные сборки из базы данных
            self.cursor.execute("""
                SELECT id, Название_сборки, Общая_цена 
                FROM "Сборки" 
                WHERE Статус_сборки = 'Активная' AND id_пользователя = %s
            """, (self.get_user_id(),))
            builds = self.cursor.fetchall()

            if not builds:
                self.active_builds_list.addItem("У вас нет активных сборок.")
            else:
                for build in builds:
                    build_id, build_name, total_price = build
                    item_text = f"{build_name} — {total_price} руб."
                    item = QListWidgetItem(item_text)
                    item.setData(1, build_id)  # Сохраняем ID сборки
                    self.active_builds_list.addItem(item)

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить сборки: {e}")


class BuildEditor(QWidget):
    def __init__(self, parent, build_id, build_name, total_price):
        super().__init__(parent)
        self.build_id = build_id
        self.setWindowTitle("Редактирование сборки")
        layout = QVBoxLayout()

        # Поле для редактирования названия
        self.name_input = QLineEdit()
        self.name_input.setText(build_name)
        layout.addWidget(QLabel("Название сборки:"))
        layout.addWidget(self.name_input)

        # Кнопка "Сохранить"
        save_button = QPushButton("Сохранить")
        save_button.clicked.connect(self.save_changes)
        layout.addWidget(save_button)

        self.setLayout(layout)

    def save_changes(self):
        new_name = self.name_input.text()
        try:
            self.parent().cursor.execute("""
                UPDATE "Сборки" 
                SET Название_сборки = %s
                WHERE id = %s
            """, (new_name, self.build_id))
            self.parent().db.conn.commit()
            QMessageBox.information(self, "Успех", "Сборка обновлена.")
            self.close()
            self.parent().show_active_builds()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка при сохранении изменений: {e}")


class AuthWindow(QWidget):
    def __init__(self, parent, mode="login"):
        super().__init__()
        self.parent = parent
        self.mode = mode
        self.setWindowTitle("Регистрация" if mode == "register" else "Вход")

        # Интерфейс окна
        layout = QVBoxLayout()

        self.info_label = QLabel("Введите логин и пароль")
        layout.addWidget(self.info_label)

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Логин")
        layout.addWidget(self.username_input)

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Пароль")
        self.password_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.password_input)

        self.submit_button = QPushButton("Зарегистрироваться" if mode == "register" else "Войти")
        self.submit_button.clicked.connect(self.handle_auth)
        layout.addWidget(self.submit_button)

        self.setLayout(layout)

    import bcrypt

    def handle_auth(self):
        username = self.username_input.text()
        password = self.password_input.text()

        if not username or not password:
            QMessageBox.warning(self, "Ошибка", "Пожалуйста, введите логин и пароль")
            return

        try:
            if self.mode == "register":
                # Регистрация пользователя в PostgreSQL
                hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())  # Хешируем пароль
                self.parent.cursor.execute(
                    "INSERT INTO Пользователи (Никнейм, Пароль, Дата_регистрации) VALUES (%s, %s, CURRENT_DATE)",
                    (username, hashed_password.decode('utf-8'))
                )
                self.parent.db.conn.commit()
                QMessageBox.information(self, "Успех", "Регистрация прошла успешно!")
                self.close()
            elif self.mode == "login":
                # Проверка пользователя
                self.parent.cursor.execute(
                    "SELECT Пароль FROM Пользователи WHERE Никнейм = %s", (username,)
                )
                result = self.parent.cursor.fetchone()

                if result:
                    stored_password = result[0]  # Пароль из базы данных
                    # Проверяем введённый пароль с хешированным
                    if bcrypt.checkpw(password.encode('utf-8'), stored_password.encode('utf-8')):
                        QMessageBox.information(self, "Успех", "Вы успешно вошли в профиль")
                        self.parent.login_user(username)
                        self.close()
                    else:
                        QMessageBox.warning(self, "Ошибка", "Неправильный логин или пароль")
                else:
                    QMessageBox.warning(self, "Ошибка", "Пользователь с таким логином не найден")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Произошла ошибка: {e}")

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
