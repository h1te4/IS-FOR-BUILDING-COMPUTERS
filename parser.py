from selenium.webdriver.common.by import By
from selenium import webdriver
import time


def main():
    driver = webdriver.Chrome()
    link = 'https://www.regard.ru/catalog/1001/processory'
    driver.set_window_size(2160, 1280)
    driver.maximize_window()

    driver.get(link)
    time.sleep(2)

    el = driver.find_element(By.CSS_SELECTOR, "#__next > div > div.LayoutWrapper_wrap__cXGc8 > main > div > div.Col_col__P83fA.Col_col-10__zuApp.Col_col-laptop-8-10__sisZ2.Col_col-tablet-12-12__67Wqn.Listing_sticky-boundary > div.Pagination_wrap__ZYNPZ.Pagination_listing__Yt5sm.pagination > div.PaginationViewChanger_countSetter__qlqiz > button > div")
    el.click()
    time.sleep(0.2)
    el = driver.find_element(By.CSS_SELECTOR, "#__next > div > div.LayoutWrapper_wrap__cXGc8 > main > div > div.Col_col__P83fA.Col_col-10__zuApp.Col_col-laptop-8-10__sisZ2.Col_col-tablet-12-12__67Wqn.Listing_sticky-boundary > div.Pagination_wrap__ZYNPZ.Pagination_listing__Yt5sm.pagination > div.PaginationViewChanger_countSetter__qlqiz > div > div:nth-child(4)")
    el.click()
    time.sleep(3)

    while True:
        try:
            el = driver.find_element(By.CLASS_NAME, "Pagination_loadMore__u1Wm_")
            el.click()
            time.sleep(2)
            print("1")
        except:
            print("2")
            break



    element = driver.find_elements(By.CLASS_NAME,
                                  "Card_row__6_JG5")
    processors = []

    for i in range(len(element)):
        text = element[i].text.split(sep="\n")
        if text[1] == "Хит продаж":
            text.pop(1)
        proccesor = [text[1], text[2].split(sep=',')[0], text[-2]]
        processors.append(proccesor)

    for i in processors:
        print(f"Название: {i[0]}")
        print(f"Сокет: {i[1]}")
        print(f"Цена: {i[2]}", '\n')

if __name__ == '__main__':
    main()
