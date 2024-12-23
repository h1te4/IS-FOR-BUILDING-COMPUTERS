from selenium.webdriver.common.by import By
from selenium import webdriver
import psycopg2
from dotenv import load_dotenv
import os
import time

# Загрузка переменных окружения
load_dotenv()

DB_HOST = os.getenv("DB_HOST")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_PORT = os.getenv("DB_PORT")

def connect_to_db():
    """Функция для подключения к базе данных."""
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            port=DB_PORT
        )
        print("Успешное подключение к базе данных")
        return conn
    except Exception as e:
        print("Ошибка подключения к базе данных:", e)
        exit()

def create_table(cur):
    """Создание таблицы компонентов, если её нет."""
    cur.execute("""
        CREATE TABLE IF NOT EXISTS "Компоненты" (
            id SERIAL PRIMARY KEY,
            "Категория" VARCHAR(255) NOT NULL,
            "Название" VARCHAR(255) UNIQUE NOT NULL,
            "Цена" NUMERIC(10, 2) NOT NULL,
            "Описание" TEXT
        )
    """)

def parse_processors():
    """Функция для парсинга процессоров."""
    driver = webdriver.Chrome()
    link = 'https://www.regard.ru/catalog/1001/processory'
    driver.set_window_size(2160, 1280)
    driver.maximize_window()

    driver.get(link)
    time.sleep(2)

    # Установка на показ всех товаров на странице
    el = driver.find_element(By.CSS_SELECTOR, "#__next > div > div.LayoutWrapper_wrap__cXGc8 > main > div > div.Col_col__P83fA.Col_col-10__zuApp.Col_col-laptop-8-10__sisZ2.Col_col-tablet-12-12__67Wqn.Listing_sticky-boundary > div.Pagination_wrap__ZYNPZ.Pagination_listing__Yt5sm.pagination > div.PaginationViewChanger_countSetter__qlqiz > button > div")
    el.click()
    time.sleep(0.2)
    el = driver.find_element(By.CSS_SELECTOR, "#__next > div > div.LayoutWrapper_wrap__cXGc8 > main > div > div.Col_col__P83fA.Col_col-10__zuApp.Col_col-laptop-8-10__sisZ2.Col_col-tablet-12-12__67Wqn.Listing_sticky-boundary > div.Pagination_wrap__ZYNPZ.Pagination_listing__Yt5sm.pagination > div.PaginationViewChanger_countSetter__qlqiz > div > div:nth-child(4)")
    el.click()
    time.sleep(3)

    # Загрузка всех товаров
    while True:
        try:
            el = driver.find_element(By.CLASS_NAME, "Pagination_loadMore__u1Wm_")
            el.click()
            time.sleep(2)
        except:
            break

    # Получение данных о процессорах
    element = driver.find_elements(By.CLASS_NAME, "Card_row__6_JG5")
    processors = []

    for i in range(len(element)):
        text = element[i].text.split(sep="\n")
        if "Хит продаж" in text:
            text.remove("Хит продаж")
        if "Новинка" in text:
            text.remove("Новинка")
        print(text)

        processor = [text[1], text[2].split(sep=',')[0], text[-2]]
        processors.append(processor)

    driver.quit()
    return processors

def insert_or_update_data(cur, processors):
    """Добавление или обновление данных в базе."""
    for processor in processors:
        cur.execute("""
            INSERT INTO "Компоненты" ("Категория", "Название", "Цена", "Описание")
            VALUES (%s, %s, %s, %s)
            ON CONFLICT ("Название") 
            DO UPDATE SET 
                "Цена" = EXCLUDED."Цена",
                "Описание" = EXCLUDED."Описание",
                "Категория" = EXCLUDED."Категория"
        """, (
            "Процессор",  # Категория
            processor[0],  # Название
            float(processor[2].replace(" ", "").replace("₽", "")),  # Цена
            processor[1]   # Описание (сокет)
        ))

def main():
    # Подключение к базе данных
    conn = connect_to_db()
    cur = conn.cursor()

    # Создание таблицы
    create_table(cur)

    # Парсинг данных
    processors = parse_processors()

    # Добавление или обновление данных
    insert_or_update_data(cur, processors)

    # Сохранение изменений и закрытие соединения
    conn.commit()
    cur.close()
    conn.close()
    print("Данные успешно добавлены или обновлены.")

if __name__ == '__main__':
    main()
