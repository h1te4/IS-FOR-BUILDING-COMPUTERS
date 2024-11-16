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


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Информационная система для сборки ПК")
        self.setGeometry(100, 100, 800, 600)

        # Атрибут для текущей категории
        self.current_category = None  # Инициализация

        # Инициализация переменной для хранения общей стоимости сборки
        self.total_price = 0

        # Словарь для отслеживания выбранных компонентов и их цен
        self.selected_components = {}

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
            conn = psycopg2.connect(
                dbname="ИС",
                user="postgres",
                password="35900956",
                host="localhost",
                port="5432"
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
        self.component_buttons = {}  # Словарь для хранения кнопок

        components = [
            ("Видеокарта", "Видеокарта"),
            ("Процессор", "Процессор"),
            ("Мат. плата", "Материнская плата"),
            ("Корпус", "Корпус"),
            ("Охлаждение процессора", "Охлаждения процессора"),
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
            self.component_buttons[category] = btn  # Сохраняем кнопку в словарь

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

    def update_build_price(self):
        """Метод для обновления общей цены сборки"""
        self.total_price = sum(self.selected_components.values())  # Суммируем только уникальные компоненты
        self.build_price_label.setText(f"Цена: {self.total_price} руб.")

    def select_component(self, item):
        """Обработка двойного клика на элемент списка компонентов"""
        try:
            # Извлекаем название компонента и его цену
            component_info = item.text().split('\n')
            selected_component = component_info[0].split(': ')[1]  # Название компонента
            component_price = float(component_info[1].split(': ')[1].split(' ')[0])  # Цена компонента

            # Если компонент уже был выбран в этой категории, вычитаем его цену
            if self.current_category in self.selected_components:
                old_component = self.selected_components[self.current_category]
                old_price = old_component  # Извлекаем старую цену
                self.total_price -= old_price  # Вычитаем старую цену

            # Обновляем или добавляем новый компонент в выбранной категории
            self.selected_components[self.current_category] = component_price  # Храним только цену

            # Добавляем цену нового компонента
            self.total_price += component_price

            # Обновляем цену сборки
            self.update_build_price()

            # Обновляем текст на кнопке для отображения текущего выбранного компонента
            for category, btn in self.component_buttons.items():
                if self.current_category == category:  # Проверяем текущую категорию
                    btn.setText(f"{category}\n{selected_component}")
                    break
        except Exception as e:
            print(f"Ошибка при выборе компонента: {e}")

    def show_components_for_category(self, category):
        """Отображение компонентов для выбранной категории на вкладке 'Новая сборка'"""
        try:
            self.current_category = category  # Обновляем текущую категорию
            self.cursor.execute("SELECT category, name, price, description FROM components WHERE category = %s",
                                (category,))
            components = self.cursor.fetchall()

            # Проверка на пустой результат
            if not components:
                print(f"Компоненты для категории '{category}' не найдены.")
                self.new_build_list.clear()
                return

            # Очищаем старый список компонентов
            self.new_build_list.clear()

            for component in components:
                # Формируем строку: категория + название
                item_text = f"{component[0]}: {component[1]}\nЦена: {component[2]} руб.\nОписание: {component[3]}"
                item = QListWidgetItem(item_text)
                self.new_build_list.addItem(item)
        except Exception as e:
            print(f"Ошибка при загрузке компонентов: {e}")

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
