import sys
import psycopg2
import bcrypt
import os
from decimal import Decimal
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
    QListWidgetItem,
    QComboBox,
    QFormLayout
)
from PyQt5.QtGui import QIcon
from datetime import datetime

load_dotenv()

DB_CONFIG = {
    'dbname': os.getenv('DB_NAME'),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'host': os.getenv('DB_HOST'),
    'port': os.getenv('DB_PORT')
}

def add_component_to_db(category, name, price, description):
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()

        # Определяем таблицу на основе категории
        table_mapping = {
            "Видеокарта": "Видеокарты",
            "Процессор": "Процессоры",
            "Материнская плата": "Материнская плата",
            "Корпус": "Корпус",
            "Охлаждение процессора": "Охлаждение процессора",
            "Оперативная память": "Оперативная память",
            "Накопитель": "Накопители",
            "Блок питания": "Блоки_питания",
            "Доп. детали": "Доп детали"
        }

        table_name = table_mapping.get(category)
        if not table_name:
            raise ValueError(f"Категория '{category}' не поддерживается.")

        # Формируем запрос
        query = f"""
            INSERT INTO "{table_name}" ("Название", "Цена", "Описание")
            VALUES (%s, %s, %s)
        """
        cursor.execute(query, (name, price, description))
        conn.commit()

        cursor.close()
        conn.close()
        print(f"{category} '{name}' добавлен в таблицу '{table_name}'.")
    except Exception as e:
        print(f"Ошибка добавления компонента: {e}")

def create_profile_button(self):
    profile_button = QPushButton()
    profile_button.setIcon(QIcon("man.png"))
    profile_button.setFixedSize(50, 50)   # Размер кнопки
    profile_button.setStyleSheet("border: none;")  # Убираем рамку вокруг кнопки
    profile_button.clicked.connect(self.show_profile_screen)  # Переход в профиль
    return profile_button


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
        self.db = Database()
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

        self.central_widget.setCurrentWidget(self.main_menu)
        # Экран завершённых сборок
        self.finished_builds_screen = self.create_finished_builds_screen()
        self.central_widget.addWidget(self.finished_builds_screen)

        # Добавляем кнопку профиля
        self.add_profile_button()

    def create_profile_button(self):
        # Создаем кнопку с картинкой для профиля
        profile_button = QPushButton()
        profile_button.setIcon(QIcon("man.png"))
        profile_button.setFixedSize(50, 50) # Размер кнопки
        profile_button.setStyleSheet("border: none;")  # Убираем рамку вокруг кнопки
        profile_button.clicked.connect(self.show_profile_screen)  # Переход в профиль
        return profile_button

    def add_profile_button(self):
        # Создаем макет для кнопки профиля
        top_layout = QHBoxLayout()
        profile_button = self.create_profile_button()  # Получаем кнопку профиля
        top_layout.addWidget(profile_button)
        top_layout.addStretch()  # Добавляем отступ справа

    def create_profile_screen(self):
        """Создание экрана профиля."""
        screen = QWidget()
        layout = QVBoxLayout()

        # Верхняя панель с кнопкой назад
        top_bar = QHBoxLayout()
        back_button = QPushButton()
        back_button.setIcon(QIcon("back.png"))
        back_button.setFixedSize(50, 50)
        back_button.clicked.connect(self.show_main_menu_screen)  # Переход в главное меню
        top_bar.addWidget(back_button)
        top_bar.addStretch()  # Отодвигает элементы вправо
        layout.addLayout(top_bar)

        # Проверяем, авторизован ли пользователь
        if self.is_user_logged_in():
            # Информация о пользователе
            profile_info = QLabel(f"Никнейм: {self.username}\nДата регистрации: {self.registration_date}")
            layout.addWidget(profile_info)

            # Кнопка выхода
            logout_button = QPushButton("Выход")
            logout_button.clicked.connect(self.logout)  # Выход из профиля
            layout.addWidget(logout_button)
        else:
            # Сообщение для неавторизованных пользователей
            profile_info = QLabel("Вы не вошли в профиль")
            layout.addWidget(profile_info)

            # Кнопка регистрации
            register_button = QPushButton("Регистрация")
            register_button.clicked.connect(self.open_registration_window)  # Открытие окна регистрации
            layout.addWidget(register_button)

            # Кнопка входа
            login_button = QPushButton("Вход")
            login_button.clicked.connect(self.open_login_window)  # Открытие окна входа
            layout.addWidget(login_button)

        # Устанавливаем layout для экрана
        screen.setLayout(layout)
        return screen

    # Проверка зарегистрирован ли пользователь
    def is_user_logged_in(self):
        return self.username is not None

    def get_user_id(self):
        if not self.username:
            print("Пользователь не авторизован: self.username = None")
            return None
        self.cursor.execute("SELECT id_Пользователя FROM Пользователи WHERE Никнейм = %s", (self.username,))
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
        self.central_widget.removeWidget(self.central_widget.widget(0))  # Удаляет старый профиль
        self.central_widget.insertWidget(0, self.profile_screen)  # Вставляет новый профиль
        self.central_widget.setCurrentWidget(self.profile_screen)  # Переключат на новый профиль

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
        self.show_active_builds()

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
            lambda: self.central_widget.setCurrentWidget(self.active_builds_screen))

        btn_finished_builds = QPushButton("Завершённые сборки")
        btn_finished_builds.clicked.connect(lambda: [self.show_finished_builds(), self.central_widget.setCurrentWidget(self.finished_builds_screen)])

        # Добавляет кнопки в макет
        for btn in [btn_new_build, btn_components, btn_active_builds, btn_finished_builds]:
            btn.setFixedHeight(50)
            buttons_layout.addWidget(btn)

        layout.addLayout(buttons_layout)
        screen.setLayout(layout)
        return screen

    def create_finished_builds_screen(self):
        """Создание экрана завершённых сборок"""
        screen = QWidget()
        layout = QVBoxLayout()

        self.finished_builds_list = QListWidget()
        layout.addWidget(self.finished_builds_list)

        back_button = QPushButton()
        back_button.setIcon(QIcon("back.png"))
        back_button.setFixedSize(50, 50)
        back_button.clicked.connect(self.show_main_menu_screen)
        layout.addWidget(back_button)

        screen.setLayout(layout)
        return screen

    def create_new_build_screen(self, mode="new", build_name="", total_price=0):
        """Создание экрана сборки (новой или для редактирования)."""
        print(f"Создаём экран сборки. Режим: {mode}, Название: {build_name}, Цена: {total_price}")  # Отладка

        screen = QWidget()
        layout = QVBoxLayout()

        # Верхняя панель
        top_bar = QHBoxLayout()
        back_btn = QPushButton()
        back_btn.setIcon(QIcon("back.png"))
        back_btn.setFixedSize(60, 40)
        back_btn.clicked.connect(lambda: self.central_widget.setCurrentWidget(self.main_menu))

        # Устанавливаем заголовок окна в зависимости от режима
        title_label = QLabel("Редактирование сборки" if mode == "edit" else "Новая сборка")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        save_btn = QPushButton("Сохранить")
        save_btn.clicked.connect(self.save_build)  # Обработчик для кнопки "Сохранить"

        delete_btn = QPushButton("Удалить")
        delete_btn.clicked.connect(self.delete_build)  # Обработчик для кнопки "Удалить"

        profile_btn = QPushButton()
        profile_btn.setIcon(QIcon("man.png"))
        profile_btn.setIconSize(profile_btn.sizeHint())
        profile_btn.setFixedSize(50, 50)
        profile_btn.clicked.connect(self.show_profile_screen)  # Добавлен обработчик для кнопки Профиль

        top_bar.addWidget(back_btn)
        top_bar.addWidget(title_label)
        top_bar.addStretch()
        if mode == "edit":  # Кнопка "Удалить" только в режиме редактирования
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

        # Список компонентов для сборки
        self.new_build_list = QListWidget()
        self.new_build_list.itemDoubleClicked.connect(self.select_component)  # Обработчик двойного клика
        layout.addWidget(self.new_build_list)

        # Метка для отображения цены сборки
        self.build_price_label = QLabel(f"Цена: {total_price} руб.")  # Устанавливаем общую цену
        layout.addWidget(self.build_price_label)

        # Нижняя панель с названием сборки
        bottom_bar = QHBoxLayout()
        new_build_label = QLabel("Название сборки: ")
        self.build_name_input = QLineEdit(
            build_name)  # Поле для ввода названия сборки (предзаполняем для редактирования)
        self.build_name_input.setPlaceholderText("Введите название сборки...")
        bottom_bar.addWidget(new_build_label)
        bottom_bar.addWidget(self.build_name_input)

        layout.addLayout(bottom_bar)  # Добавляет нижнюю панель в layout

        screen.setLayout(layout)
        return screen

    def save_build(self):
        """Сохранение сборки в базу данных."""
        # Проверка, авторизован ли пользователь
        if not self.is_user_logged_in():
            QMessageBox.warning(self, "Ошибка", "Вы должны войти в профиль, чтобы сохранить сборку!")
            return

        build_name = self.build_name_input.text()

        # Проверка, чтобы название сборки не было пустым
        if not build_name.strip():
            QMessageBox.warning(self, "Ошибка", "Пожалуйста, введите название сборки!")
            return

        try:
            # Вставляем сборку в таблицу "Сборки"
            self.cursor.execute(
                """
                INSERT INTO "Сборки" ("Название_сборки", "Общая_цена", "id_Пользователя", "Статус_сборки") 
                VALUES (%s, %s, %s, %s) RETURNING "id_сборки"
                """,
                (build_name, self.total_price, self.get_user_id(), 'Активная')
            )
            build_id = self.cursor.fetchone()[0]  # Получаем id_сборки
            print(f"ID новой сборки: {build_id}")  # Отладка

            # Сохраняем компоненты для этой сборки в таблицу "Компоненты_сборки"
            for category, component_name in self.selected_components.items():
                print(
                    f"Добавляем компонент для сборки {build_id}, категория: {category}, компонент: {component_name}")  # Отладка

                # Заполняем таблицу "Компоненты_сборки"
                query = f"""
                UPDATE "Компоненты_сборки" SET "{category}" = %s WHERE "id_сборки" = %s
                """
                self.cursor.execute(query, (component_name, build_id))

            self.db.conn.commit()
            self.show_active_builds()  # Обновляем окно активных сборок
            QMessageBox.information(self, "Успех", "Сборка успешно сохранена!")
        except Exception as e:
            self.db.conn.rollback()
            print(f"Ошибка при сохранении сборки: {e}")  # Отладка ошибки
            QMessageBox.critical(self, "Ошибка", f"Ошибка при сохранении сборки: {e}")

    def delete_build(self, build_id):
        """Удаление сборки из базы данных."""
        try:
            # Удаляем сборку по ID
            self.cursor.execute(
                """
                DELETE FROM "Сборки" 
                WHERE "id_сборки" = %s
                """,
                (build_id,)
            )
            self.db.conn.commit()
            QMessageBox.information(self, "Успех", "Сборка успешно удалена.")
            self.show_active_builds()  # Перезагружает список активных сборок
        except Exception as e:
            self.db.conn.rollback()  # Откатываем изменения в случае ошибки
            QMessageBox.critical(self, "Ошибка", f"Ошибка при удалении сборки: {e}")

    def show_finished_builds(self):
        """Отображение завершённых сборок"""
        try:
            # Очищаем список перед загрузкой
            self.finished_builds_list.clear()

            # Получаем ID текущего пользователя
            user_id = self.get_user_id()
            if user_id is None:
                QMessageBox.warning(self, "Ошибка", "Вы должны войти в профиль, чтобы видеть завершённые сборки!")
                return

            # Выполняем запрос к базе данных для получения завершённых сборок
            self.cursor.execute("""
                SELECT "Название_сборки", "Общая_цена"
                FROM "Сборки"
                WHERE "Статус_сборки" = 'Завершенная' AND "id_Пользователя" = %s
            """, (user_id,))
            builds = self.cursor.fetchall()

            # Если сборок нет, отображаем сообщение
            if not builds:
                self.finished_builds_list.addItem("У вас нет завершённых сборок.")
                return

            # Добавляем завершённые сборки в список
            for build_name, total_price in builds:
                self.finished_builds_list.addItem(f"{build_name} — {total_price} руб.")

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить завершённые сборки: {e}")

    def edit_build(self, build_id):
        """Редактирование сборки."""
        try:
            print(f"Редактирование сборки с ID {build_id}")  # Отладка
            self.cursor.execute("""
                SELECT "Название_сборки", "Общая_цена"
                FROM "Сборки"
                WHERE "id_сборки" = %s
            """, (build_id,))
            build = self.cursor.fetchone()

            if build:
                build_name, total_price = build
                print(f"Открываем окно редактирования для сборки: {build_name}, Цена: {total_price}")  # Отладка

                # Открываем экран редактирования сборки
                self.edit_build_screen = self.create_new_build_screen(
                    mode="edit",
                    build_name=build_name,
                    total_price=total_price
                )
                self.central_widget.setCurrentWidget(self.edit_build_screen)  # Переход на экран редактирования
            else:
                QMessageBox.warning(self, "Ошибка", "Сборка не найдена.")
        except Exception as e:
            print(f"Ошибка при редактировании сборки: {e}")  # Отладка
            QMessageBox.critical(self, "Ошибка", f"Ошибка при редактировании сборки: {e}")

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
        """Отображение компонентов для выбранной категории."""
        self.current_category = category

        try:
            # Проверяем, подключена ли база данных
            if self.db.conn.closed:
                self.db = Database()  # Повторное подключение
                self.cursor = self.db.cursor

            # Сопоставление категорий с таблицами
            table_mapping = {
                "Видеокарта": "Видеокарты",
                "Процессор": "Процессоры",
                "Материнская плата": "Материнская плата",
                "Корпус": "Корпус",
                "Охлаждение процессора": "Охлаждение процессора",
                "Оперативная память": "Оперативная память",
                "Накопитель": "Накопители",
                "Блок питания": "Блоки_питания",
                "Доп. детали": "Доп детали"
            }

            # Получаем таблицу для категории
            table_name = table_mapping.get(category)
            if not table_name:
                print(f"Категория '{category}' не найдена в сопоставлении.")
                self.new_build_list.clear()
                self.new_build_list.addItem(QListWidgetItem("Категория не найдена."))
                return

            # Выполняем запрос к нужной таблице
            query = f"""
                SELECT "Название", "Цена", "Описание"
                FROM "{table_name}"
            """
            self.cursor.execute(query)
            components = self.cursor.fetchall()

            # Проверяем, есть ли данные
            if not components or len(components) == 0:
                print(f"Нет данных для категории '{category}'.")
                self.new_build_list.clear()
                self.new_build_list.addItem(QListWidgetItem("Нет компонентов в этой категории."))
                return

            # Очищаем список и добавляем компоненты
            self.new_build_list.clear()
            for component in components:
                try:
                    # Проверяем структуру данных
                    if len(component) != 3:
                        raise ValueError(f"Некорректные данные компонента: {component}")

                    name, price, description = component

                    # Преобразуем цену из Decimal в float
                    if not isinstance(price, (int, float, Decimal)):
                        raise ValueError(f"Неверный тип данных для цены: {price}")
                    price = float(price)

                    # Формируем текст элемента
                    item_text = f"{category}: {name}\nЦена: {price} руб.\nОписание: {description}"
                    self.new_build_list.addItem(QListWidgetItem(item_text))

                except ValueError as ve:
                    print(f"Пропущен компонент: {ve}")


        except Exception as e:
            print(f"Ошибка при загрузке компонентов: {e}")

    def create_components_screen(self):
        """Создание экрана склада комплектующих"""
        screen = QWidget()
        layout = QVBoxLayout()

        # Кнопка "Добавить"
        add_button = QPushButton("Добавить")
        add_button.setFixedHeight(50)
        add_button.clicked.connect(self.show_add_component_screen)  # Открыть окно добавления
        layout.addWidget(add_button)

        self.components_list = QListWidget()
        self.load_and_display_all_components()
        layout.addWidget(self.components_list)

        screen.setLayout(layout)
        return screen

    def show_add_component_screen(self):
        try:
            print("Переход на экран добавления комплектующих")  # Отладка
            self.add_component_screen = self.create_add_component_screen()
            self.central_widget.addWidget(self.add_component_screen)
            self.central_widget.setCurrentWidget(self.add_component_screen)
            print("Экран добавления комплектующих успешно открыт")  # Отладка
        except Exception as e:
            print(f"Ошибка в show_add_component_screen: {e}")  # Отладка ошибки

    def create_add_component_screen(self):
        """Создание экрана добавления комплектующих"""
        screen = QWidget()
        layout = QVBoxLayout()

        self.name_input = QLineEdit()  # Вместо локальной переменной

        # Верхняя панель с кнопкой "Назад"
        top_bar = QHBoxLayout()
        back_button = QPushButton()
        back_button.setIcon(QIcon("back.png"))
        back_button.setFixedSize(50, 50)
        back_button.clicked.connect(lambda: self.central_widget.setCurrentWidget(self.components_screen))
        top_bar.addWidget(back_button)

        title_label = QLabel("Добавление комплектующих")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        top_bar.addWidget(title_label)
        top_bar.addStretch()
        layout.addLayout(top_bar)

        # Выбор категории
        category_label = QLabel("Выберите категорию:")
        self.category_combo = QComboBox()
        self.category_combo.addItems([
            "Видеокарта", "Процессор", "Материнская плата", "Корпус",
            "Охлаждение процессора", "Оперативная память", "Накопитель",
            "Блок питания", "Доп. детали"
        ])
        self.category_combo.currentTextChanged.connect(self.update_form_fields)
        layout.addWidget(category_label)
        layout.addWidget(self.category_combo)

        # Форма для ввода данных
        self.form_layout = QFormLayout()
        layout.addLayout(self.form_layout)
        self.update_form_fields("Видеокарта")  # Устанавливаем поля по умолчанию

        # Кнопка "Сохранить"
        save_button = QPushButton("Сохранить")
        save_button.clicked.connect(self.save_component)
        layout.addWidget(save_button)

        screen.setLayout(layout)
        return screen

    def update_form_fields(self, category):
        """Обновление полей формы в зависимости от выбранной категории"""
        # Очистить текущие поля
        while self.form_layout.count():
            child = self.form_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        # Общие поля
        self.name_input = QLineEdit()
        self.description_input = QLineEdit()
        self.price_input = QLineEdit()
        self.form_layout.addRow("Название:", self.name_input)
        self.form_layout.addRow("Описание:", self.description_input)

        # Уникальные поля для каждой категории
        if category == "Процессор" or category == "Материнская плата":
            self.socket_input = QLineEdit()
            self.form_layout.addRow("Сокет:", self.socket_input)
        if category == "Накопитель":
            self.capacity_input = QLineEdit()
            self.form_layout.addRow("Объём:", self.capacity_input)
        if category == "Блок питания":
            self.power_input = QLineEdit()
            self.form_layout.addRow("Мощность:", self.power_input)

        # Поле "Цена" для всех категорий
        self.form_layout.addRow("Цена:", self.price_input)

    def save_component(self):
        """Сохранение нового компонента в базу данных"""
        try:
            # Получаем данные из формы
            category = self.category_combo.currentText()
            name = self.name_input.text()
            description = self.description_input.text()
            price = Decimal(self.price_input.text())

            # Уникальные поля
            socket = self.socket_input.text() if hasattr(self, "socket_input") else None
            capacity = self.capacity_input.text() if hasattr(self, "capacity_input") else None
            power = self.power_input.text() if hasattr(self, "power_input") else None

            # Определяем таблицу
            table_mapping = {
                "Видеокарта": "Видеокарты",
                "Процессор": "Процессоры",
                "Материнская плата": "Материнская плата",
                "Корпус": "Корпус",
                "Охлаждение процессора": "Охлаждение процессора",
                "Оперативная память": "Оперативная память",
                "Накопитель": "Накопители",
                "Блок питания": "Блоки_питания",
                "Доп. детали": "Доп детали"
            }
            table_name = table_mapping.get(category)

            # Формируем SQL-запрос
            query = f"""
                INSERT INTO "{table_name}" ("Название", "Описание", {f'"Сокет", ' if socket else ''}{f'"Объём", ' if capacity else ''}{f'"Мощность", ' if power else ''}"Цена")
                VALUES (%s, %s, {f'%s, ' if socket else ''}{f'%s, ' if capacity else ''}{f'%s, ' if power else ''}%s)
            """
            values = [name, description]
            if socket:
                values.append(socket)
            if capacity:
                values.append(capacity)
            if power:
                values.append(power)
            values.append(price)

            # Выполняем запрос
            self.cursor.execute(query, values)
            self.db.conn.commit()

            QMessageBox.information(self, "Успех", f"{category} добавлена в базу данных!")
            self.central_widget.setCurrentWidget(self.components_screen)  # Возврат на экран "Склад комплектующих"
            self.load_and_display_all_components()  # Обновляем список компонентов
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка при добавлении компонента: {e}")

    def load_and_display_all_components(self):
        """Загрузка всех компонентов из всех категорий для отображения"""
        try:
            # Сопоставление категорий с таблицами
            table_mapping = {
                "Видеокарты": "Видеокарта",
                "Процессоры": "Процессор",
                "Материнская плата": "Материнская плата",
                "Корпус": "Корпус",
                "Охлаждение процессора": "Охлаждение процессора",
                "Оперативная память": "Оперативная память",
                "Накопители": "Накопитель",
                "Блоки_питания": "Блок питания",
                "Доп детали": "Доп. детали"
            }

            self.components_list.clear()  # Очищаем список перед загрузкой

            for table, category in table_mapping.items():
                # Запрашиваем данные из каждой таблицы
                self.cursor.execute(f"""
                    SELECT "Название", "Цена"
                    FROM "{table}"
                """)
                components = self.cursor.fetchall()

                if not components:  # Проверка, если данных нет
                    continue

                # Добавляем компоненты в список
                for component in components:
                    if len(component) < 2:  # Проверка на корректность данных
                        print(f"Некорректные данные в таблице {table}: {component}")
                        continue

                    name, price = component
                    item_text = f"{category}: {name}\nЦена: {price} руб."
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

        back_button = QPushButton()
        back_button.setIcon(QIcon("back.png"))
        back_button.setFixedSize(50, 50)
        back_button.clicked.connect(self.show_main_menu_screen)
        layout.addWidget(back_button)

        # Вызов метода для отображения активных сборок
        self.show_active_builds()

        screen.setLayout(layout)
        return screen

    def show_active_builds(self):
        """Отображение активных сборок."""
        try:
            # Очищает список перед обновлением
            self.active_builds_list.clear()

            # Получает ID текущего пользователя
            user_id = self.get_user_id()
            if user_id is None:
                print("Пользователь не авторизован.")
                QMessageBox.warning(self, "Ошибка", "Вы должны войти в профиль, чтобы видеть активные сборки!")
                return

            print(f"Выполняем запрос для получения активных сборок для пользователя с ID {user_id}...")
            self.cursor.execute("""
                SELECT "id_сборки", "Название_сборки", "Общая_цена"
                FROM "Сборки"
                WHERE "Статус_сборки" = 'Активная' AND "id_Пользователя" = %s
            """, (user_id,))
            builds = self.cursor.fetchall()

            print(f"Найдено активных сборок: {len(builds)}")

            # Если сборок нет
            if not builds:
                self.active_builds_list.addItem("У вас нет активных сборок.")
                return

            # Добавляет сборки с кнопками в список
            for build_id, build_name, total_price in builds:
                # Создаёт виджет для строки
                row_widget = QWidget()
                row_layout = QHBoxLayout()  # Горизонтальный макет для строки
                row_layout.setContentsMargins(5, 5, 5, 5)  # Отступы

                # Добавляет текст сборки
                build_label = QLabel(f"{build_name} — {total_price} руб.")
                row_layout.addWidget(build_label)

                # Кнопка "Редактировать"
                edit_button = QPushButton("Редактировать")
                edit_button.setFixedSize(100, 30)
                edit_button.clicked.connect(lambda _, b_id=build_id: self.edit_build(b_id))  # Привязываем к методу
                row_layout.addWidget(edit_button)

                # Кнопка "Завершить"
                complete_button = QPushButton("Завершить")
                complete_button.clicked.connect(lambda _, b_id=build_id: self.finish_build(b_id))
                complete_button.setFixedSize(100, 30)

  # Привязываем к методу
                row_layout.addWidget(complete_button)

                # Кнопка "Удалить"
                delete_button = QPushButton("Удалить")
                delete_button.setFixedSize(100, 30)
                delete_button.clicked.connect(lambda _, b_id=build_id: self.delete_build(b_id))  # Привязываем к методу
                row_layout.addWidget(delete_button)

                # Устанавливает макет в виджет
                row_widget.setLayout(row_layout)

                # Добавляет виджет строки в QListWidget через QListWidgetItem
                list_item = QListWidgetItem()
                list_item.setSizeHint(row_widget.sizeHint())  # Устанавливает размер строки
                self.active_builds_list.addItem(list_item)
                self.active_builds_list.setItemWidget(list_item, row_widget)

                # Отладка
                print(f"Добавлена сборка: {build_name} с ID {build_id}")

        except Exception as e:
            print(f"Ошибка при загрузке активных сборок: {e}")
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

    def handle_auth(self):
        """Обработка входа или регистрации."""
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()

        if not username or not password:
            QMessageBox.warning(self, "Ошибка", "Введите логин и пароль")
            return

        try:
            if self.mode == "login":
                # Проверяем, существует ли пользователь
                self.parent.cursor.execute("SELECT Пароль FROM Пользователи WHERE Никнейм = %s", (username,))
                result = self.parent.cursor.fetchone()

                if not result:
                    QMessageBox.warning(self, "Ошибка", "Пользователь с таким логином не найден")
                    return

                stored_password = result[0]
                if bcrypt.checkpw(password.encode('utf-8'), stored_password.encode('utf-8')):
                    QMessageBox.information(self, "Успех", "Вы успешно вошли")
                    self.parent.login_user(username)  # Логиним пользователя в родительском классе
                    self.close()
                else:
                    QMessageBox.warning(self, "Ошибка", "Неправильный пароль")

            elif self.mode == "register":
                # Проверяем, существует ли пользователь
                self.parent.cursor.execute("SELECT 1 FROM Пользователи WHERE Никнейм = %s", (username,))
                if self.parent.cursor.fetchone():
                    QMessageBox.warning(self, "Ошибка", "Пользователь с таким никнеймом уже существует")
                    return

                # Регистрация нового пользователя
                hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
                self.parent.cursor.execute(
                    "INSERT INTO Пользователи (Никнейм, Пароль, Дата_регистрации) VALUES (%s, %s, CURRENT_DATE)",
                    (username, hashed_password)
                )
                self.parent.db.conn.commit()
                QMessageBox.information(self, "Успех", "Вы успешно зарегистрировались")
                self.close()

        except Exception as e:
            self.parent.db.conn.rollback()
            print(f"Ошибка: {e}")
            QMessageBox.critical(self, "Ошибка", f"Произошла ошибка: {e}")



    def login(self, username, password):
        # Пример логики аутентификации
        self.cursor.execute(
            "SELECT id_Пользователя FROM Пользователи WHERE Никнейм = %s AND Пароль = %s",
            (username, password),
        )
        result = self.cursor.fetchone()
        if result:
            self.username = username
            return True
        else:
            return False

    def get_user_id(self):
        if not self.username:
            return None
        self.cursor.execute("SELECT id_Пользователя FROM Пользователи WHERE Никнейм = %s", (self.username,))
        result = self.cursor.fetchone()
        return result[0] if result else None

    def handle_registration(self):
        """Обработка регистрации пользователя."""
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()

        if not username or not password:
            QMessageBox.warning(self, "Ошибка", "Введите логин и пароль")
            return

        try:
            # Проверяем, существует ли пользователь
            self.parent.cursor.execute("SELECT 1 FROM Пользователи WHERE Никнейм = %s", (username,))
            if self.parent.cursor.fetchone():
                QMessageBox.warning(self, "Ошибка", "Пользователь с таким никнеймом уже существует")
                return

            # Регистрируем нового пользователя
            hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            self.parent.cursor.execute(
                "INSERT INTO Пользователи (Никнейм, Пароль, Дата_регистрации) VALUES (%s, %s, CURRENT_DATE)",
                (username, hashed_password)
            )
            self.parent.db.conn.commit()
            QMessageBox.information(self, "Успех", "Вы успешно зарегистрировались")
            self.close()
        except Exception as e:
            self.parent.db.conn.rollback()
            print(f"Ошибка регистрации: {e}")
            QMessageBox.critical(self, "Ошибка", f"Ошибка регистрации: {e}")

    def handle_login(self):
        """Обработка входа пользователя."""
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()

        if not username or not password:
            QMessageBox.warning(self, "Ошибка", "Введите логин и пароль")
            return

        try:
            # Проверяем, существует ли пользователь
            self.parent.cursor.execute("SELECT Пароль FROM Пользователи WHERE Никнейм = %s", (username,))
            result = self.parent.cursor.fetchone()
            print(f"Результат проверки пользователя: {result}")  # Отладка

            if not result:
                QMessageBox.warning(self, "Ошибка", "Пользователь с таким логином не найден")
                return

            # Проверяем пароль
            stored_password = result[0]
            if bcrypt.checkpw(password.encode('utf-8'), stored_password.encode('utf-8')):
                QMessageBox.information(self, "Успех", "Вы успешно вошли")
                self.parent.login_user(username)  # Передаём имя пользователя в MainWindow
                self.close()
            else:
                QMessageBox.warning(self, "Ошибка", "Неправильный пароль")
        except Exception as e:
            print(f"Ошибка входа: {e}")
            QMessageBox.critical(self, "Ошибка", f"Ошибка при входе: {e}")


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