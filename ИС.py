import sys
import psycopg2
import bcrypt
import os
from decimal import Decimal
from dotenv import load_dotenv
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QStackedWidget,
    QGridLayout,
    QHBoxLayout,
    QPushButton,
    QWidget,
    QVBoxLayout,
    QLabel,
    QMessageBox,
    QListWidget,
    QListWidgetItem,
    QLineEdit,
    QComboBox,
    QFormLayout
)
from PyQt5.QtGui import QIcon

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
    def __init__(self, connection, parent=None):
        super(MainWindow, self).__init__(parent)
        self.connection = connection
        self.cursor = self.connection.cursor()

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Информационная система для сборки ПК")
        self.setGeometry(100, 100, 800, 600)

        # Переменная для хранения общей стоимости сборки
        self.total_price = 0

        # Начальные значения никнейма и даты регистрации
        self.username = None
        self.registration_date = None

        # Словарь для отслеживания выбранных компонентов
        self.selected_components = {}

        # Подключение к базе данных через объект Database
        self.db = Database()
        self.cursor = self.db.cursor

        # Основной стек виджетов
        self.central_widget = QStackedWidget()
        self.setCentralWidget(self.central_widget)

        # Экраны приложения
        self.main_menu = self.create_main_menu()  # Главный экран
        self.components_screen = self.create_components_screen()  # Экран склада комплектующих
        self.profile_screen = self.create_profile_screen()  # Экран профиля
        self.new_build_screen = self.create_new_build_screen()  # Экран новой сборки
        self.finished_builds_screen = self.create_finished_builds_screen()  # Экран завершённых сборок

        # Добавляем экраны в стек
        self.central_widget.addWidget(self.main_menu)
        self.central_widget.addWidget(self.components_screen)
        self.central_widget.addWidget(self.profile_screen)
        self.central_widget.addWidget(self.new_build_screen)
        self.central_widget.addWidget(self.finished_builds_screen)

        # Устанавливаем главный экран
        self.central_widget.setCurrentWidget(self.main_menu)

        # Для добавления компонентов в сборку
        self.add_to_build_screen = None
        self.builds_combo_box = None


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
        # Создание экрана профиля
        screen = QWidget()
        self.profile_layout = QVBoxLayout()  # Основной макет

        # === Верхняя панель ===
        top_bar = QHBoxLayout()
        back_button = QPushButton()
        back_button.setIcon(QIcon("back.png"))
        back_button.setFixedSize(50, 50)
        back_button.clicked.connect(self.show_main_menu_screen)  # Возврат на главный экран
        top_bar.addWidget(back_button)
        top_bar.addStretch()

        # Заголовок "Профиль"
        title_label = QLabel("Профиль")
        title_label.setAlignment(Qt.AlignCenter)  # Центрируем текст
        title_label.setStyleSheet("font-size: 24px; font-weight: bold; margin: 20px;")  # Стилизация текста
        self.profile_layout.addLayout(top_bar)
        self.profile_layout.addWidget(title_label)

        # === Информация о профиле ===
        self.profile_info = QLabel()  # Используем QLabel для отображения данных
        self.profile_info.setStyleSheet("font-size: 18px; font-weight: normal;")
        self.profile_info.setAlignment(Qt.AlignLeft)  # Текст выравнивается влево
        self.profile_layout.addWidget(self.profile_info)

        # Макет для кнопок входа/выхода
        self.profile_buttons_layout = QVBoxLayout()  # Сохраняем для динамического изменения кнопок
        self.profile_layout.addLayout(self.profile_buttons_layout)

        # Устанавливаем основной макет для экрана
        screen.setLayout(self.profile_layout)

        # Заполняем данные профиля
        self.update_profile_screen()
        return screen

    def update_profile_screen(self):
        # Обновление данных на экране профиля и текстовой информации
        self.profile_info.setText(
            f"Никнейм: {self.username}\nДата регистрации: {self.registration_date}"
            if self.is_user_logged_in()
            else "Вы не вошли в профиль"
        )

        # Удаляем старые кнопки
        for i in reversed(range(self.profile_buttons_layout.count())):
            widget = self.profile_buttons_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()

        # Добавляем кнопки в зависимости от статуса пользователя
        if self.is_user_logged_in():
            logout_button = QPushButton("Выход")
            logout_button.clicked.connect(self.logout)  # Связь кнопки с методом выхода
            self.profile_buttons_layout.addWidget(logout_button)
        else:
            register_button = QPushButton("Регистрация")
            register_button.clicked.connect(self.open_registration_window)
            login_button = QPushButton("Вход")
            login_button.clicked.connect(self.open_login_window)
            self.profile_buttons_layout.addWidget(register_button)
            self.profile_buttons_layout.addWidget(login_button)

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

    def logout(self):
        #Выход из профиля
        self.username = None
        self.registration_date = None
        self.update_profile_screen()

    def login_user(self, username):
        #Вход пользователя
        self.username = username
        self.registration_date = self.get_registration_date(username)
        self.update_profile_screen()
        self.central_widget.setCurrentWidget(self.profile_screen)

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
        # Вход пользователя
        self.username = username
        self.registration_date = self.get_registration_date(username)
        self.update_profile_screen()  # Обновление информации на экране профиля
        self.central_widget.setCurrentWidget(self.profile_screen)  # Переключение на экран профиля

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
            # Хешируем пароль перед сохранением
            hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

            # Добавляем пользователя в базу данных
            self.db.execute_query(
                "INSERT INTO Пользователи (Никнейм, Пароль, Дата_регистрации) VALUES (%s, %s, CURRENT_DATE)",
                (username, hashed_password)
            )

            # Успешная регистрация
            QMessageBox.information(self, "Успех", "Регистрация успешна!")

            # Автоматический вход в профиль
            self.login_user(username)  # Используем метод для авторизации пользователя

            # Переключаемся на экран профиля
            self.central_widget.setCurrentWidget(self.profile_screen)
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", "Ошибка регистрации: пользователь уже существует!")

    def show_profile_screen(self):
        self.central_widget.setCurrentWidget(self.profile_screen)

    def create_main_menu(self):
        # Создание главного меню
        screen = QWidget()
        main_layout = QVBoxLayout()

        # Верхняя панель
        top_layout = QHBoxLayout()
        profile_btn = QPushButton()  # Создание кнопки профиля
        profile_btn.setIcon(QIcon("man.png"))  # Устанавливаем иконку
        profile_btn.setIconSize(profile_btn.sizeHint())  # Задаём размер иконки
        profile_btn.setFixedSize(50, 50)  # Устанавливаем фиксированный размер кнопки
        profile_btn.clicked.connect(self.show_profile_screen)  # Обработчик для открытия экрана профиля

        top_layout.addStretch()  # Добавляем отступ слева
        top_layout.addWidget(profile_btn)  # Добавляем кнопку профиля

        # Центральная панель с кнопками
        buttons_layout = QGridLayout()  # Используем сетку для размещения кнопок
        buttons_layout.setContentsMargins(50, 50, 50, 50)  # Отступы вокруг кнопок (слева, сверху, справа, снизу)
        buttons_layout.setHorizontalSpacing(100)  # Горизонтальное расстояние между кнопками
        buttons_layout.setVerticalSpacing(80)  # Вертикальное расстояние между кнопками

        # Создание кнопок
        btn_new_build = QPushButton("Новая сборка")
        btn_new_build.setMinimumSize(200, 70)  # Устанавливаем минимальный размер кнопки
        btn_new_build.clicked.connect(lambda: self.central_widget.setCurrentWidget(self.new_build_screen))

        btn_components = QPushButton("Склад комплектующих")
        btn_components.setMinimumSize(200, 70)
        btn_components.clicked.connect(lambda: self.central_widget.setCurrentWidget(self.components_screen))

        btn_active_builds = QPushButton("Активные сборки")
        btn_active_builds.setMinimumSize(200, 70)
        btn_active_builds.clicked.connect(self.show_active_builds_screen)

        btn_finished_builds = QPushButton("Завершённые сборки")
        btn_finished_builds.setMinimumSize(200, 70)
        btn_finished_builds.clicked.connect(
            lambda: [self.show_finished_builds(), self.central_widget.setCurrentWidget(self.finished_builds_screen)]
        )

        # Расположение кнопок в сетке
        buttons_layout.addWidget(btn_new_build, 0, 0)  # Первая кнопка (верхний левый угол)
        buttons_layout.addWidget(btn_components, 0, 1)  # Вторая кнопка (верхний правый угол)
        buttons_layout.addWidget(btn_active_builds, 1, 0)  # Третья кнопка (нижний левый угол)
        buttons_layout.addWidget(btn_finished_builds, 1, 1)  # Четвёртая кнопка (нижний правый угол)

        # Собираем основной макет
        main_layout.addLayout(top_layout)  # Верхняя панель
        main_layout.addStretch()  # Отступ перед центральной панелью
        main_layout.addLayout(buttons_layout)  # Центральная панель (с кнопками навигации)
        main_layout.addStretch()  # Отступ после центральной панели

        screen.setLayout(main_layout)
        return screen

    def create_finished_builds_screen(self):
        # Создание экрана завершённых сборок
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

    def finish_build(self, build_id):
        try:
            print(f"Завершаем сборку с ID: {build_id}")

            # Проверяем, есть ли соединение с базой данных
            if self.db.conn.closed:
                self.db = Database()  # Повторное подключение
                self.cursor = self.db.cursor

            # Обновляем статус сборки на 'Завершена'
            self.cursor.execute("""
                UPDATE "Сборки"
                SET "Статус_сборки" = 'Завершена'
                WHERE "id_сборки" = %s
            """, (build_id,))
            self.db.conn.commit()
            QMessageBox.information(self, "Успех", "Сборка завершена успешно.")
            self.load_active_builds()  # Обновление экрана активных сборок
        except Exception as e:
            self.db.conn.rollback()
            QMessageBox.critical(self, "Ошибка", f"Не удалось завершить сборку: {e}")

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось завершить сборку: {e}")

    def create_new_build_screen(self, build_name="", total_price=0, is_edit=False, build_id=None):
        # Создаёт экран для новой или редактируемой сборки.
        # Создание виджета и основного макета
        screen = QWidget()
        layout = QVBoxLayout()

        # Верхняя панель
        top_bar = QHBoxLayout()

        # Кнопка "Назад"
        back_button = QPushButton()
        back_button.setIcon(QIcon("back.png"))
        back_button.setFixedSize(60, 40)
        back_button.clicked.connect(lambda: self.central_widget.setCurrentWidget(self.main_menu))

        # Заголовок
        title_label = QLabel("Редактирование сборки" if is_edit else "Новая сборка")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold;")

        # Кнопка "Сохранить"
        save_btn = QPushButton("Сохранить")
        save_btn.clicked.connect(lambda: self.save_build(is_edit=is_edit, build_id=build_id))

        # Кнопка "Отменить"
        cancel_btn = QPushButton("Отменить")
        cancel_btn.clicked.connect(self.cancel_selection)

        # Кнопка "Профиль"
        profile_btn = QPushButton()
        profile_btn.setIcon(QIcon("man.png"))
        profile_btn.setFixedSize(50, 50)
        profile_btn.clicked.connect(self.show_profile_screen)

        # Добавление элементов верхней панели
        top_bar.addWidget(back_button)
        top_bar.addWidget(title_label)
        top_bar.addStretch()
        top_bar.addWidget(save_btn)
        top_bar.addWidget(cancel_btn)
        top_bar.addWidget(profile_btn)
        layout.addLayout(top_bar)

        # Секция выбора компонентов
        components_layout = QHBoxLayout()
        self.component_buttons = {}

        components = [
            ("Видеокарта", "Видеокарта"),
            ("Процессор", "Процессор"),
            ("Мат. плата", "Материнская плата"),
            ("Корпус", "Корпус"),
            ("Охлаждение процессора", "Охлаждение процессора"),
            ("Оперативная память", "Оперативная память"),
            ("Накопители", "Накопитель"),
            ("Блок питания", "Блок питания"),
            ("Доп. детали", "Доп. детали"),
        ]

        # Кнопки для выбора категорий
        for label, category in components:
            btn = QPushButton(label)
            btn.setFixedHeight(40)
            btn.clicked.connect(lambda checked, c=category: self.show_components_for_category(c))
            components_layout.addWidget(btn)
            self.component_buttons[category] = btn

        layout.addLayout(components_layout)

        # Список компонентов для сборки
        self.new_build_list = QListWidget()
        self.new_build_list.itemDoubleClicked.connect(self.select_component)
        layout.addWidget(self.new_build_list)

        # Метка для отображения цены
        self.build_price_label = QLabel(f"Цена: {total_price} руб.")
        layout.addWidget(self.build_price_label)

        # Нижняя панель с названием сборки
        bottom_bar = QHBoxLayout()
        new_build_label = QLabel("Название сборки: ")
        self.build_name_input = QLineEdit(build_name)
        self.build_name_input.setPlaceholderText("Введите название сборки...")
        bottom_bar.addWidget(new_build_label)
        bottom_bar.addWidget(self.build_name_input)

        layout.addLayout(bottom_bar)
        screen.setLayout(layout)
        return screen

    def cancel_selection(self):
        # Очищаем все выбранные компоненты
        self.selected_components.clear()  # Очищаем словарь выбранных компонентов
        self.new_build_list.clear()  # Очищаем список компонентов

        # Сбрасываем цену
        self.total_price = 0  # Устанавливаем цену в 0
        self.build_price_label.setText(f"Цена: {self.total_price} руб.")  # Обновляем текст метки с ценой

        # Сбрасываем текст на кнопках категорий
        for category, button in self.component_buttons.items():
            button.setText(category)  # Восстанавливаем исходный текст кнопок категорий

        print("Выбор компонентов отменен. Цена сброшена, текст на кнопках сброшен.")

    def save_build(self, is_edit=False, build_id=None):
        # Сохраняет новую сборку или обновляет существующую.
        if not self.is_user_logged_in():
            QMessageBox.warning(self, "Ошибка", "Вы должны войти в профиль, чтобы сохранить сборку!")
            return

        build_name = self.build_name_input.text().strip()

        if not build_name:
            QMessageBox.warning(self, "Ошибка", "Пожалуйста, введите название сборки!")
            return

        try:
            print(f"Начинаем сохранение сборки. Название: {build_name}, Общая цена: {self.total_price}")
            if is_edit and build_id:
                print(f"Обновляем сборку с ID {build_id}")
                # Обновление существующей сборки
                self.cursor.execute("""
                    UPDATE "Сборки"
                    SET "Название_сборки" = %s, "Общая_цена" = %s
                    WHERE "id_сборки" = %s
                """, (build_name, self.total_price, build_id))
            else:
                print("Создаём новую сборку")
                # Создание новой сборки
                self.cursor.execute("""
                    INSERT INTO "Сборки" ("Название_сборки", "Общая_цена", "id_Пользователя", "Статус_сборки")
                    VALUES (%s, %s, %s, %s) RETURNING "id_сборки"
                """, (build_name, self.total_price, self.get_user_id(), 'Активная'))
                build_id = self.cursor.fetchone()[0]

            # Обновляем компоненты сборки
            for category, component in self.selected_components.items():
                print(f"Обрабатываем категорию: {category}, компонент: {component}")

                if isinstance(component, dict):
                    component_name = component.get("Название")
                else:
                    component_name = component

                if not component_name:
                    raise ValueError(f"Для категории {category} не выбран компонент.")

                # Проверяем, существует ли запись для обновления
                self.cursor.execute(f"""
                    SELECT 1 FROM "Компоненты_сборки"
                    WHERE "id_сборки" = %s AND "{category}" IS NOT NULL
                """, (build_id,))
                if self.cursor.fetchone():
                    print(f"Обновляем компонент в категории {category}: {component_name}")
                    # Обновляем существующую запись
                    self.cursor.execute(f"""
                        UPDATE "Компоненты_сборки"
                        SET "{category}" = %s
                        WHERE "id_сборки" = %s
                    """, (component_name, build_id))
                else:
                    print(f"Добавляем новый компонент в категории {category}: {component_name}")
                    # Добавляем новую запись
                    self.cursor.execute(f"""
                        INSERT INTO "Компоненты_сборки" ("id_сборки", "{category}")
                        VALUES (%s, %s)
                    """, (build_id, component_name))

            # Сохраняем изменения в базе данных
            print("Сохраняем изменения в базе данных...")
            self.db.conn.commit()

            QMessageBox.information(self, "Успех", "Сборка успешно сохранена!")
            self.show_active_builds_screen()

        except ValueError as ve:
            print(f"Ошибка: {ve}")
            QMessageBox.warning(self, "Ошибка", str(ve))
        except Exception as e:
            print(f"Ошибка при сохранении сборки: {e}")
            self.db.conn.rollback()
            QMessageBox.critical(self, "Ошибка", f"Ошибка при сохранении сборки: {e}")

    def delete_build(self, build_id):
        # Удаление сборки из базы данных
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
            self.show_active_builds_screen()  # Перезагружает список активных сборок
        except Exception as e:
            self.db.conn.rollback()  # Откатываем изменения в случае ошибки
            QMessageBox.critical(self, "Ошибка", f"Ошибка при удалении сборки: {e}")

    def show_finished_builds(self):
        # Отображение завершённых сборок
        try:
            # Очищаем список перед загрузкой
            self.finished_builds_list.clear()

            # Получаем ID текущего пользователя
            user_id = self.get_user_id()

            # Проверяем, авторизован ли пользователь
            if user_id is None:  # Предполагаем, что None — это неавторизованный пользователь
                self.finished_builds_list.addItem("Вы не авторизованы!")
                return

            # Выполняем запрос к базе данных для получения завершённых сборок
            self.cursor.execute("""
                SELECT "Название_сборки", "Общая_цена"
                FROM "Сборки"
                WHERE "Статус_сборки" = 'Завершена' AND "id_Пользователя" = %s
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
        # Открывает экран для редактирования сборки.
        try:
            self.cursor.execute("""
                SELECT "Название_сборки", "Общая_цена"
                FROM "Сборки"
                WHERE "id_сборки" = %s
            """, (build_id,))
            build_data = self.cursor.fetchone()

            if not build_data:
                QMessageBox.warning(self, "Ошибка", "Сборка не найдена.")
                return

            build_name, total_price = build_data

            self.cursor.execute("""
                SELECT "Процессор", "Видеокарта", "Материнская плата", "Корпус",
                       "Охлаждение процессора", "Оперативная память", "Накопитель",
                       "Блок питания", "Доп. детали"
                FROM "Компоненты_сборки"
                WHERE "id_сборки" = %s
            """, (build_id,))
            component_data = self.cursor.fetchone()

            categories = [
                "Процессор", "Видеокарта", "Материнская плата", "Корпус",
                "Охлаждение процессора", "Оперативная память", "Накопитель",
                "Блок питания", "Доп. детали",
            ]

            self.selected_components = {
                category: component for category, component in zip(categories, component_data) if component
            }

            edit_screen = self.create_new_build_screen(
                build_name=build_name,
                total_price=total_price,
                is_edit=True,
                build_id=build_id
            )

            self.central_widget.addWidget(edit_screen)
            self.central_widget.setCurrentWidget(edit_screen)

            for category, component in self.selected_components.items():
                if category in self.component_buttons:
                    self.component_buttons[category].setText(f"{category}\n{component}")

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить сборку: {e}")

    def create_edit_build_screen(self, build_id, build_name="", total_price=0):
        print(f"Создаём экран редактирования для сборки: {build_name} (ID: {build_id})")  # Отладка

        screen = QWidget()
        layout = QVBoxLayout()

        # Верхняя панель
        top_bar = QHBoxLayout()
        back_button = QPushButton()
        back_button.setIcon(QIcon("back.png"))
        back_button.setFixedSize(60, 40)
        back_button.clicked.connect(self.show_active_builds_screen)

        title_label = QLabel("Редактирование сборки")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold;")

        save_btn = QPushButton("Сохранить")
        save_btn.clicked.connect(self.save_build)  # Обработчик для сохранения

        cancel_btn = QPushButton("Отменить")
        cancel_btn.clicked.connect(self.cancel_selection)  # Очистка выбора компонентов

        top_bar.addWidget(back_button)
        top_bar.addWidget(title_label)
        top_bar.addStretch()
        top_bar.addWidget(save_btn)
        top_bar.addWidget(cancel_btn)

        # Секция выбора комплектующих
        components_layout = QHBoxLayout()
        self.component_buttons = {}

        components = [
            ("Видеокарта", "Видеокарта"),
            ("Процессор", "Процессор"),
            ("Мат. плата", "Материнская плата"),
            ("Корпус", "Корпус"),
            ("Охлаждение процессора", "Охлаждение процессора"),
            ("Оперативная память", "Оперативная память"),
            ("Накопители", "Накопитель"),
            ("Блок питания", "Блок питания"),
            ("Доп. детали", "Доп. детали"),
        ]

        for label, category in components:
            btn = QPushButton(label)
            btn.setFixedHeight(40)
            if category in self.selected_components:
                btn.setText(f"{label}\n{self.selected_components[category]}")
            btn.clicked.connect(lambda checked, c=category: self.show_components_for_category(c))
            components_layout.addWidget(btn)
            self.component_buttons[category] = btn

        layout.addLayout(top_bar)
        layout.addLayout(components_layout)

        # Метка для отображения цены сборки
        self.build_price_label = QLabel(f"Цена: {total_price} руб.")
        layout.addWidget(self.build_price_label)

        # Поле для редактирования названия сборки
        bottom_bar = QHBoxLayout()
        new_build_label = QLabel("Название сборки: ")
        self.build_name_input = QLineEdit(build_name)
        bottom_bar.addWidget(new_build_label)
        bottom_bar.addWidget(self.build_name_input)

        layout.addLayout(bottom_bar)
        screen.setLayout(layout)
        return screen

    def save_changes(self):
        try:
            # Получаем значения выбранных компонентов из комбобоксов
            updated_components = {}
            for category in ["Процессоры", "Видеокарты", "Материнская плата", "Корпус",
                             "Охлаждение процессора", "Оперативная память", "Накопители",
                             "Блоки_питания", "Доп. детали"]:
                combo_box = self.central_widget.findChild(QComboBox, category)
                selected_component = combo_box.currentText()
                updated_components[category] = selected_component

            # Обновляем данные в базе для текущей сборки
            self.cursor.execute("""
                UPDATE "Компоненты_сборки"
                SET "Процессор" = %s, "Видеокарта" = %s, "Материнская плата" = %s,
                    "Корпус" = %s, "Охлаждение процессора" = %s, "Оперативная память" = %s,
                    "Накопитель" = %s, "Блок питания" = %s, "Доп. детали" = %s
                WHERE "id_сборки" = %s
            """, (
                updated_components["Процессор"],
                updated_components["Видеокарта"],
                updated_components["Материнская плата"],
                updated_components["Корпус"],
                updated_components["Охлаждение процессора"],
                updated_components["Оперативная память"],
                updated_components["Накопитель"],
                updated_components["Блок питания"],
                updated_components["Доп. детали"],
                self.current_build_id
            ))

            # Подтверждаем изменения в базе данных
            self.connection.commit()

            # Показываем сообщение об успешном сохранении
            QMessageBox.information(self, "Успех", "Изменения успешно сохранены!")

            # Возвращаемся на экран с активными сборками (или любой другой нужный экран)
            self.show_active_builds_screen()

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось сохранить изменения: {e}")

    def select_component_from_list(self, category):
        # Открываем экран для выбора компонента из базы данных
        self.cursor.execute(f"""
            SELECT "Название", "Описание", "Цена"
            FROM "{category}"  -- Пример: Видеокарты, Процессоры и т.д.
        """)
        components = self.cursor.fetchall()

        # Создаем экран для выбора компонента
        selection_screen = QWidget()
        layout = QVBoxLayout()
        selection_screen.setLayout(layout)

        # Заголовок для категории
        category_label = QLabel(f"Выберите {category}")
        layout.addWidget(category_label)

        # Список компонентов
        for component_name, description, price in components:
            button = QPushButton(f"{component_name} — {price} руб.")
            button.clicked.connect(
                lambda _, comp_name=component_name: self.update_selected_component(comp_name, category))
            layout.addWidget(button)

        # Добавляем экран в центральный виджет и показываем
        self.central_widget.addWidget(selection_screen)
        self.central_widget.setCurrentWidget(selection_screen)

    def update_selected_component(self, component_name, category):
        # Обновляем выбранный компонент для категории
        self.selected_components[category] = component_name

        # Обновляем текст кнопки категории
        self.update_category_button(category)

        # Возвращаемся на экран редактирования сборки
        self.return_to_edit_screen()

    def update_category_button(self, category):
        # Находим кнопку для выбранной категории и обновляем ее текст
        buttons = self.central_widget.findChildren(QPushButton)
        for button in buttons:
            if button.text().startswith(category):
                button.setText(f"{category}: {self.selected_components[category]}")

    def return_to_edit_screen(self):
        # Возвращаемся к экрану редактирования сборки
        self.central_widget.setCurrentWidget(self.central_widget.widget(0))

    def open_build_editor(self, build_id, build_name, total_price):
        editor_window = BuildEditor(self, build_id, build_name, total_price)
        editor_window.show()

    def select_component(self, item):
        # Выбирает компонент для текущей категории.
        try:
            # Получаем текст из элемента списка
            lines = item.text().split("\n")
            component_name = lines[0].split(": ")[1]

            # Проверяем, есть ли уже выбранный компонент в текущей категории
            old_price = 0
            if self.current_category in self.selected_components:
                selected_component = self.selected_components[self.current_category]
                # Проверяем, является ли компонент словарём
                if isinstance(selected_component, dict):
                    old_price = selected_component.get("Цена", 0)
                else:
                    # Если сохранён компонент в виде строки, очищаем старое значение
                    old_price = 0

            # Удаляем старую цену из общей суммы
            self.total_price -= old_price

            # Получаем данные о компоненте из базы данных
            self.cursor.execute(f"""
                SELECT "Цена"
                FROM "{self.current_category}"
                WHERE "Название" = %s
            """, (component_name,))
            price_data = self.cursor.fetchone()

            if not price_data:
                QMessageBox.warning(self, "Ошибка", f"Компонент {component_name} не найден в базе данных.")
                return

            component_price = price_data[0]

            # Обновляем выбранный компонент
            self.selected_components[self.current_category] = {
                "Название": component_name,
                "Цена": component_price
            }

            # Добавляем новую цену к общей сумме
            self.total_price += component_price

            # Обновляем текст кнопки для категории
            if self.current_category in self.component_buttons:
                self.component_buttons[self.current_category].setText(f"{self.current_category}\n{component_name}")

            # Обновляем отображение общей цены
            self.update_build_price()

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка при выборе компонента: {e}")

    def update_build_price(self):
        # Обновление общей цены сборки
        self.build_price_label.setText(f"Цена: {self.total_price} руб.")

    def show_components_for_category(self, category):
        # Отображение компонентов для выбранной категории
        self.current_category = category

        try:
            # Проверяем, подключена ли база данных
            if self.db.conn.closed:
                self.db = Database()  # Повторное подключение
                self.cursor = self.db.cursor

            # Сопоставление категорий с таблицами и характеристиками
            category_mapping = {
                "Видеокарта": {
                    "table": "Видеокарты",
                    "fields": ["Название", "Цена", "Описание"]
                },
                "Процессор": {
                    "table": "Процессоры",
                    "fields": ["Название", "Цена", "Описание", "Сокет"]
                },
                "Материнская плата": {
                    "table": "Материнская плата",
                    "fields": ["Название", "Цена", "Описание", "Сокет", "Размер"]
                },
                "Корпус": {
                    "table": "Корпус",
                    "fields": ["Название", "Цена", "Описание", "Размер"]
                },
                "Охлаждение процессора": {
                    "table": "Охлаждение процессора",
                    "fields": ["Название", "Цена", "Описание"]
                },
                "Оперативная память": {
                    "table": "Оперативная память",
                    "fields": ["Название", "Цена", "Описание", "Тип_памяти"]
                },
                "Накопитель": {
                    "table": "Накопители",
                    "fields": ["Название", "Цена", "Описание", "Объём"]
                },
                "Блок питания": {
                    "table": "Блоки_питания",
                    "fields": ["Название", "Цена", "Описание", "Мощность"]
                },
                "Доп. детали": {
                    "table": "Доп детали",
                    "fields": ["Название", "Цена", "Описание"]
                }
            }

            # Получаем информацию для выбранной категории
            category_info = category_mapping.get(category)
            if not category_info:
                print(f"Категория '{category}' не найдена в сопоставлении.")
                self.new_build_list.clear()
                self.new_build_list.addItem(QListWidgetItem("Категория не найдена."))
                return

            table_name = category_info["table"]
            fields = category_info["fields"]

            # Выполняем запрос к нужной таблице
            query = f"""
                SELECT {', '.join(fields)}
                FROM "{table_name}"
            """
            self.cursor.execute(query)
            components = self.cursor.fetchall()

            # Проверяем, есть ли данные
            if not components:
                print(f"Нет данных для категории '{category}'.")
                self.new_build_list.clear()
                self.new_build_list.addItem(QListWidgetItem("Нет компонентов в этой категории."))
                return

            # Очищаем список и добавляем компоненты
            self.new_build_list.clear()
            for component in components:
                component_data = dict(zip(fields, component))

                # Преобразуем цену из Decimal в float, если нужно
                price = float(component_data["Цена"])

                # Формируем текст элемента для списка
                item_text = f"{category}: {component_data['Название']}\nЦена: {price} руб.\nОписание: {component_data['Описание']}"
                for field in fields:
                    if field not in ["Название", "Цена", "Описание"]:
                        item_text += f"\n{field}: {component_data[field]}"

                list_item = QListWidgetItem(item_text)
                self.new_build_list.addItem(list_item)

                # Привязываем данные компонента к элементу списка для использования при выборе
                list_item.setData(Qt.UserRole, component_data)

            # Отключаем старые соединения и подключаем обработчик выбора компонента
            try:
                self.new_build_list.itemClicked.disconnect()
            except TypeError:
                pass
            self.new_build_list.itemClicked.connect(self.select_component)

        except Exception as e:
            print(f"Ошибка при загрузке компонентов: {e}")

    def create_components_screen(self):
        # Создаёт экран склада комплектующих
        screen = QWidget()
        screen.setObjectName("components_screen")

        # Главный layout
        layout = QVBoxLayout()

        # Верхняя панель с кнопками "Назад" и "Профиль"
        top_bar = QHBoxLayout()

        # Кнопка "Назад"
        back_btn = QPushButton()
        back_btn.setIcon(QIcon("back.png"))
        back_btn.setFixedSize(50, 50)
        back_btn.clicked.connect(lambda: self.central_widget.setCurrentWidget(self.main_menu))
        top_bar.addWidget(back_btn)

        # Добавляем пустое пространство между кнопками
        top_bar.addStretch()

        # Кнопка "Профиль"
        profile_btn = QPushButton()
        profile_btn.setIcon(QIcon("man.png"))  # Убедитесь, что файл man.png существует
        profile_btn.setFixedSize(50, 50)  # Размер кнопки
        profile_btn.clicked.connect(self.show_profile_screen)  # Переход в профиль
        top_bar.addWidget(profile_btn)  # Добавляем кнопку "Профиль" в top_bar

        # Добавляем top_bar в основной layout
        layout.addLayout(top_bar)

        # === Кнопка "Добавить комплектующее" ===
        add_component_button = QPushButton("Добавить комплектующее")
        add_component_button.setFixedHeight(40)  # Устанавливаем высоту кнопки
        add_component_button.clicked.connect(self.show_add_component_screen)  # Переход на экран добавления
        layout.addWidget(add_component_button)

        # Поле для поиска
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Введите название компонента и нажмите Enter")
        self.search_bar.returnPressed.connect(self.search_components)  # Поиск выполняется по Enter
        layout.addWidget(self.search_bar)

        # Список для отображения компонентов
        self.components_list = QListWidget()
        layout.addWidget(self.components_list)

        # Устанавливаем layout для экрана
        screen.setLayout(layout)

        # Отображаем все компоненты из базы при загрузке
        self.load_and_display_all_components()

        return screen

    def show_add_component_screen(self):
        screen = self.create_add_component_screen()
        self.central_widget.addWidget(screen)
        self.central_widget.setCurrentWidget(screen)

    def search_components(self):

        # Выполняет поиск компонентов по названию, используя введённый текст
        # Если строка поиска пустая, загружает все компоненты

        search_text = self.search_bar.text().strip()  # Получаем текст из строки поиска

        if not search_text:
            # Если текст пустой, загружаем все компоненты
            self.load_and_display_all_components()
            return

        try:
            # Очищаем список перед поиском
            self.components_list.clear()

            # Сопоставление категорий с таблицами
            table_mapping = {
                "Видеокарты": "Видеокарты",
                "Процессоры": "Процессоры",
                "Материнская плата": "Материнская плата",
                "Корпус": "Корпус",
                "Охлаждение процессора": "Охлаждение процессора",
                "Оперативная память": "Оперативная память",
                "Накопители": "Накопители",
                "Блоки_питания": "Блоки_питания",
                "Доп детали": "Доп детали"
            }

            for category, table in table_mapping.items():
                # Выполняем запрос с фильтрацией
                self.cursor.execute(f"""
                    SELECT "Название", "Цена"
                    FROM "{table}"
                    WHERE "Название" ILIKE %s
                """, (f'%{search_text}%',))
                components = self.cursor.fetchall()

                if not components:
                    continue

                # Добавляем компоненты в список
                for component in components:
                    name, price = component
                    item_text = f"{category}: {name}\nЦена: {price} руб."
                    item = QListWidgetItem(item_text)
                    self.components_list.addItem(item)

        except Exception as e:
            print(f"Ошибка при поиске компонентов: {e}")

    def create_add_component_screen(self):
        # Создание экрана добавления комплектующих
        screen = QWidget()
        layout = QVBoxLayout()

        self.name_input = QLineEdit()  # Вместо локальной переменной

        # Верхняя панель с кнопкой "Назад"
        top_bar = QHBoxLayout()
        back_button = QPushButton()
        back_button.setIcon(QIcon("back.png"))
        back_button.setFixedSize(50, 50)
        back_button.clicked.connect(lambda: self.central_widget.setCurrentWidget(self.main_menu))
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
        # Обновляет поля формы в зависимости от выбранной категории.
        # Очистить текущие поля
        while self.form_layout.count():
            child = self.form_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        # Общие поля
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Введите название компонента")
        self.description_input = QLineEdit()
        self.description_input.setPlaceholderText("Введите описание компонента")
        self.price_input = QLineEdit()
        self.price_input.setPlaceholderText("Введите цену в формате 1234.56")

        self.form_layout.addRow("Название:", self.name_input)
        self.form_layout.addRow("Описание:", self.description_input)
        self.form_layout.addRow("Цена:", self.price_input)

        # Уникальные поля для каждой категории
        if category == "Процессор" or category == "Материнская плата":
            self.socket_input = QLineEdit()
            self.socket_input.setPlaceholderText("Введите сокет, например: AM4, LGA1200")
            self.form_layout.addRow("Сокет:", self.socket_input)

        if category == "Накопитель":
            self.capacity_input = QLineEdit()
            self.capacity_input.setPlaceholderText("Введите объём, например: 1TB, 512GB")
            self.form_layout.addRow("Объём:", self.capacity_input)

        if category == "Блок питания":
            self.power_input = QLineEdit()
            self.power_input.setPlaceholderText("Введите мощность в Вт, например: 650")
            self.form_layout.addRow("Мощность:", self.power_input)

        if category == "Оперативная память":
            self.memory_type_input = QLineEdit()
            self.memory_type_input.setPlaceholderText("Введите тип памяти, например: DDR4")
            self.form_layout.addRow("Тип памяти:", self.memory_type_input)

        if category in ["Материнская плата", "Корпус"]:
            self.size_input = QLineEdit()
            self.size_input.setPlaceholderText("Введите размер, например: ATX, Micro-ATX")
            self.form_layout.addRow("Размер:", self.size_input)

    def save_component(self):
        # Сохранение нового компонента в базу данных
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
        # Загрузка всех компонентов из всех категорий для отображения
        try:
            # Сопоставление категорий с таблицами и характеристиками
            table_mapping = {
                "Видеокарты": {
                    "table": "Видеокарты",
                    "fields": ["Название", "Описание", "Цена"]
                },
                "Процессоры": {
                    "table": "Процессоры",
                    "fields": ["Название", "Описание", "Сокет", "Цена"]
                },
                "Материнская плата": {
                    "table": "Материнская плата",
                    "fields": ["Название", "Сокет", "Описание", "Цена", "Размер"]
                },
                "Корпус": {
                    "table": "Корпус",
                    "fields": ["Название", "Описание", "Цена", "Размер"]
                },
                "Охлаждение процессора": {
                    "table": "Охлаждение процессора",
                    "fields": ["Название", "Описание", "Цена"]
                },
                "Оперативная память": {
                    "table": "Оперативная память",
                    "fields": ["Название", "Описание", "Цена", "Тип_памяти"]
                },
                "Накопители": {
                    "table": "Накопители",
                    "fields": ["Название", "Описание", "Цена", "Объём"]
                },
                "Блоки питания": {
                    "table": "Блоки_питания",
                    "fields": ["Название", "Мощность", "Описание", "Цена"]
                },
                "Доп. детали": {
                    "table": "Доп детали",
                    "fields": ["Название", "Описание", "Цена"]
                }
            }

            self.components_list.clear()  # Очищаем список перед загрузкой

            # Загружаем компоненты из каждой категории
            for category, category_info in table_mapping.items():
                table_name = category_info["table"]
                fields = category_info["fields"]

                # Запрашиваем данные из каждой таблицы
                query = f"""
                    SELECT {', '.join(fields)}
                    FROM "{table_name}"
                """
                self.cursor.execute(query)
                components = self.cursor.fetchall()

                if not components:  # Если данных нет, пропускаем категорию
                    continue

                # Добавляем компоненты в список
                for component in components:
                    if len(component) < 2:  # Проверка на корректность данных
                        print(f"Некорректные данные в таблице {table_name}: {component}")
                        continue

                    # Формируем словарь с данными компонента
                    component_data = dict(zip(fields, component))
                    name = component_data["Название"]
                    price = component_data["Цена"]
                    description = component_data.get("Описание", "Нет описания")

                    # Формируем строку для отображения
                    item_text = f"{category}: {name}\nЦена: {price} руб.\nОписание: {description}"

                    # Добавляем специфичные характеристики для каждой категории
                    for field in fields:
                        if field not in ["Название", "Цена", "Описание"]:
                            item_text += f"\n{field}: {component_data[field]}"

                    # Создаем виджет для компонента
                    item_widget = QWidget()
                    item_layout = QHBoxLayout()  # Горизонтальный layout для содержимого

                    # Добавляем описание компонента в текстовую метку
                    content_label = QLabel(item_text)
                    content_label.setWordWrap(True)  # Включаем перенос текста
                    content_label.setStyleSheet("font-size: 12px;")  # Можно задать стиль для текста

                    # Добавляем метку в layout
                    item_layout.addWidget(content_label)

                    # Кнопка "Добавить" справа от компонента
                    add_button = QPushButton("Добавить")
                    add_button.clicked.connect(lambda _, n=name, t=table_name: self.show_add_to_build_screen(n, t))
                    item_layout.addWidget(add_button)

                    item_widget.setLayout(item_layout)

                    # Создаем элемент списка и добавляем его
                    item = QListWidgetItem()
                    item.setSizeHint(item_widget.sizeHint())

                    self.components_list.addItem(item)
                    self.components_list.setItemWidget(item, item_widget)

        except Exception as e:
            print(f"Ошибка при загрузке компонентов: {e}")

    def show_add_to_build_screen(self, component_name, table_name):

        # Отображение окна добавления компонента в сборку.
        # Проверяет авторизацию пользователя, отображает список активных сборок.
        # Проверяем, авторизован ли пользователь
        user_id = self.get_user_id()
        if not user_id:
            QMessageBox.warning(self, "Ошибка", "Вы должны войти в профиль, чтобы добавлять комплектующие в сборку!")
            return

        # Если окно еще не создано, создаем его
        if self.add_to_build_screen is None:
            self.add_to_build_screen = QWidget()
            layout = QVBoxLayout()

            # === Верхняя панель с кнопкой "Назад" ===
            top_bar = QHBoxLayout()
            back_button = QPushButton()
            back_button.setIcon(QIcon("back.png"))  # Иконка для кнопки "Назад"
            back_button.setFixedSize(50, 50)
            back_button.clicked.connect(
                lambda: self.central_widget.setCurrentWidget(self.components_screen))  # Возврат на экран компонентов
            top_bar.addWidget(back_button)
            top_bar.addStretch()
            layout.addLayout(top_bar)  # Добавляем верхнюю панель в основной макет

            # === Отображение названия компонента ===
            self.component_label = QLabel()
            self.component_label.setStyleSheet("font-size: 18px; font-weight: bold; margin: 10px;")
            layout.addWidget(self.component_label)

            # === Выпадающий список для выбора сборки ===
            self.builds_combo_box = QComboBox()
            self.builds_combo_box.setStyleSheet("font-size: 16px; margin: 10px;")
            layout.addWidget(self.builds_combo_box)

            # === Кнопка "Добавить в сборку" ===
            add_button = QPushButton("Добавить в сборку")
            add_button.setStyleSheet("font-size: 16px; padding: 10px;")
            add_button.clicked.connect(self.add_component_to_build)
            layout.addWidget(add_button)

            # Устанавливаем макет для экрана
            self.add_to_build_screen.setLayout(layout)
            self.central_widget.addWidget(self.add_to_build_screen)

        # Устанавливаем название выбранного компонента
        self.component_label.setText(f"Компонент: {component_name}")

        # === Получаем список активных сборок ===
        self.cursor.execute("""
            SELECT id_сборки, Название_сборки
            FROM Сборки
            WHERE Статус_сборки = 'Активная' AND id_Пользователя = %s
        """, (user_id,))
        builds = self.cursor.fetchall()

        # Очищаем и заполняем выпадающий список сборок
        self.builds_combo_box.clear()
        if not builds:
            self.builds_combo_box.addItem("Нет доступных сборок", -1)
        else:
            for build in builds:
                self.builds_combo_box.addItem(build[1], build[0])

        # Устанавливаем экран добавления компонента как текущий
        self.central_widget.setCurrentWidget(self.add_to_build_screen)

    def add_component_to_build(self):
        # Добавление компонента в сборку
        try:
            # Получаем id выбранной сборки
            selected_build_id = self.builds_combo_box.currentData()
            if not selected_build_id:
                QMessageBox.warning(self, "Ошибка", "Не выбрана сборка!")
                return

            # Название компонента
            component_name = self.component_label.text().split(": ")[1]  # Из текста QLabel

            # Пример: добавляем компонент в поле "Видеокарта" (или другое)
            self.cursor.execute("""
                UPDATE "Компоненты_сборки"
                SET "Видеокарта" = %s
                WHERE "id_сборки" = %s
            """, (component_name, selected_build_id))

            self.db.conn.commit()  # Используем соединение через self.db
            QMessageBox.information(self, "Успех", "Компонент успешно добавлен в сборку!")
        except Exception as e:
            self.db.conn.rollback()  # Откатываем изменения в случае ошибки
            QMessageBox.critical(self, "Ошибка", f"Ошибка при добавлении компонента: {e}")

    def show_active_builds_screen(self):
        # Показ экрана активных сборок
        # Создаем экран
        screen = QWidget()
        layout = QVBoxLayout()
        screen.setLayout(layout)

        # Список для отображения активных сборок
        self.active_builds_list = QListWidget()
        layout.addWidget(self.active_builds_list)

        # Верхняя панель с кнопкой назад
        back_button = QPushButton()
        back_button.setIcon(QIcon("back.png"))
        back_button.setFixedSize(50, 50)
        back_button.clicked.connect(
            lambda: self.central_widget.setCurrentWidget(self.main_menu))  # Возврат в главное меню
        layout.addWidget(back_button)

        # Добавляем экран в стек виджетов, если он еще не добавлен
        if screen not in [self.central_widget.widget(i) for i in range(self.central_widget.count())]:
            self.central_widget.addWidget(screen)

        # Устанавливаем экран активных сборок как текущий
        self.central_widget.setCurrentWidget(screen)

        # Загружаем данные активных сборок
        self.load_active_builds()

    def load_active_builds(self):
        # Загрузка и отображение активных сборок с кнопками управления
        try:
            # Очищаем список перед загрузкой
            self.active_builds_list.clear()

            # Проверяем, авторизован ли пользователь
            user_id = self.get_user_id()
            if not user_id:
                self.active_builds_list.addItem("Вы не авторизованы!")
                return

            # Запрашиваем активные сборки
            self.cursor.execute("""
                SELECT "id_сборки", "Название_сборки", "Общая_цена"
                FROM "Сборки"
                WHERE "Статус_сборки" = 'Активная' AND "id_Пользователя" = %s
            """, (user_id,))
            builds = self.cursor.fetchall()

            # Если сборок нет
            if not builds:
                self.active_builds_list.addItem("У вас нет активных сборок.")
            else:
                # Заполняем список активных сборок
                for build_id, build_name, total_price in builds:
                    # Создаем виджет строки
                    row_widget = QWidget()
                    row_layout = QHBoxLayout()

                    # Добавляем текст сборки
                    build_label = QLabel(f"{build_name} — {total_price} руб.")
                    row_layout.addWidget(build_label)

                    # Кнопка "Редактировать"
                    edit_button = QPushButton("Редактировать")
                    edit_button.setFixedSize(100, 30)
                    edit_button.clicked.connect(lambda _, b_id=build_id: self.edit_build(b_id))
                    row_layout.addWidget(edit_button)

                    # Кнопка "Завершить"
                    complete_button = QPushButton("Завершить")
                    complete_button.setFixedSize(100, 30)
                    complete_button.clicked.connect(lambda _, b_id=build_id: self.finish_build(b_id))
                    row_layout.addWidget(complete_button)

                    # Кнопка "Удалить"
                    delete_button = QPushButton("Удалить")
                    delete_button.setFixedSize(100, 30)
                    delete_button.clicked.connect(lambda _, b_id=build_id: self.delete_build(b_id))
                    row_layout.addWidget(delete_button)

                    # Устанавливаем макет в виджет строки
                    row_widget.setLayout(row_layout)

                    # Создаем элемент списка и добавляем в него строку
                    list_item = QListWidgetItem()
                    list_item.setSizeHint(row_widget.sizeHint())
                    self.active_builds_list.addItem(list_item)
                    self.active_builds_list.setItemWidget(list_item, row_widget)
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить активные сборки: {e}")


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
        # Обработка входа или регистрации
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
        # Обработка регистрации пользователя
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
        # Обработка входа пользователя
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
        self.conn = psycopg2.connect(**DB_CONFIG)
        self.cursor = self.conn.cursor()

    def execute_query(self, query, params=None):
        try:
            self.cursor.execute(query, params)
            self.conn.commit()
        except Exception as e:
            self.conn.rollback()
            raise e

    def close(self):
        self.cursor.close()
        self.conn.close()

    def closeEvent(self, event):
        self.db.close()
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())