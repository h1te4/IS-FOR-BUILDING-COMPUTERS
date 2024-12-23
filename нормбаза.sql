-- Начало транзакции
BEGIN;

-- Создание последовательности для таблицы Пользователи
CREATE SEQUENCE IF NOT EXISTS public."Пользователи_id_seq";

-- Таблица Пользователи
CREATE TABLE IF NOT EXISTS public."Пользователи"
(
    "id_Пользователя" integer NOT NULL DEFAULT nextval('"Пользователи_id_seq"'::regclass),
    "Никнейм" character varying(255) NOT NULL,
    "Пароль" character varying(255) NOT NULL,
    "Дата_регистрации" date,
    CONSTRAINT "pk_пользователи" PRIMARY KEY ("id_Пользователя"),
    CONSTRAINT "уникальный_никнейм" UNIQUE ("Никнейм")
);

-- Таблица Сборки
CREATE TABLE IF NOT EXISTS public."Сборки"
(
    "id_сборки" SERIAL NOT NULL,
    "Название_сборки" character varying(255) NOT NULL,
    "Общая_цена" numeric(10, 2) NOT NULL,
    "id_Пользователя" integer NOT NULL,
    "Статус_сборки" character varying(50) NOT NULL,
    "Дата_создания" timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    "Дата_завершения" timestamp without time zone,
    CONSTRAINT "pk_сборки" PRIMARY KEY ("id_сборки"),
    CONSTRAINT "fk_пользователь" FOREIGN KEY ("id_Пользователя")
        REFERENCES public."Пользователи" ("id_Пользователя") ON DELETE CASCADE
);

-- Таблица Компоненты_сборки
CREATE TABLE IF NOT EXISTS public."Компоненты_сборки"
(
    id SERIAL NOT NULL,
    "id_сборки" integer NOT NULL,
    "Процессор" character varying(255),
    "Видеокарта" character varying(255),
    "Материнская плата" character varying(255),
    "Корпус" character varying(255),
    "Охлаждение процессора" character varying(255),
    "Оперативная память" character varying(255),
    "Накопитель" character varying(255),
    "Блок питания" character varying(255),
    "Доп. детали" character varying(255),
    CONSTRAINT "pk_компоненты_сборки" PRIMARY KEY (id),
    CONSTRAINT "fk_сборка" FOREIGN KEY ("id_сборки")
        REFERENCES public."Сборки" ("id_сборки") ON DELETE CASCADE
);

-- Таблица Процессоры
CREATE TABLE IF NOT EXISTS public."Процессоры"
(
    "Название" character varying(255) NOT NULL,
    "Описание" text NOT NULL,
    "Сокет" character varying(100) NOT NULL,
    "Цена" numeric(8, 2) NOT NULL,
    PRIMARY KEY ("Название")
);

-- Таблица Видеокарты
CREATE TABLE IF NOT EXISTS public."Видеокарты"
(
    "Название" character varying(255) NOT NULL,
    "Описание" text NOT NULL,
    "Цена" numeric(8, 2) NOT NULL,
    PRIMARY KEY ("Название")
);

-- Таблица Материнская плата
CREATE TABLE IF NOT EXISTS public."Материнская плата"
(
    "Название" character varying(255) NOT NULL,
    "Сокет" character varying(100) NOT NULL,
    "Описание" text NOT NULL,
    "Цена" numeric(8, 2) NOT NULL,
    PRIMARY KEY ("Название")
);

-- Таблица Корпус
CREATE TABLE IF NOT EXISTS public."Корпус"
(
    "Название" character varying(255) NOT NULL,
    "Описание" text NOT NULL,
    "Цена" numeric(8, 2) NOT NULL,
    PRIMARY KEY ("Название")
);

-- Таблица Охлаждение процессора
CREATE TABLE IF NOT EXISTS public."Охлаждение процессора"
(
    "Название" character varying(255) NOT NULL,
    "Описание" text NOT NULL,
    "Цена" numeric(8, 2) NOT NULL,
    PRIMARY KEY ("Название")
);

-- Таблица Оперативная память
CREATE TABLE IF NOT EXISTS public."Оперативная память"
(
    "Название" character varying(255) NOT NULL,
    "Описание" text NOT NULL,
    "Цена" numeric(8, 2) NOT NULL,
    PRIMARY KEY ("Название")
);

-- Таблица Накопители
CREATE TABLE IF NOT EXISTS public."Накопители"
(
    "Название" character varying(255) NOT NULL,
    "Объём" character varying(100) NOT NULL,
    "Описание" text NOT NULL,
    "Цена" numeric(8, 2) NOT NULL,
    PRIMARY KEY ("Название")
);

-- Таблица Блоки питания
CREATE TABLE IF NOT EXISTS public."Блоки_питания"
(
    "Название" character varying(255) NOT NULL,
    "Мощность" integer NOT NULL,
    "Описание" text NOT NULL,
    "Цена" numeric(8, 2) NOT NULL,
    PRIMARY KEY ("Название")
);

-- Таблица Доп детали
CREATE TABLE IF NOT EXISTS public."Доп детали"
(
    "Название" character varying(255) NOT NULL,
    "Описание" text NOT NULL,
    "Цена" numeric(8, 2) NOT NULL,
    PRIMARY KEY ("Название")
);

-- Внешние ключи для таблицы Компоненты_сборки
ALTER TABLE IF EXISTS public."Компоненты_сборки"
    ADD CONSTRAINT "fk_процессор" FOREIGN KEY ("Процессор")
    REFERENCES public."Процессоры" ("Название");

ALTER TABLE IF EXISTS public."Компоненты_сборки"
    ADD CONSTRAINT "fk_видеокарта" FOREIGN KEY ("Видеокарта")
    REFERENCES public."Видеокарты" ("Название");

ALTER TABLE IF EXISTS public."Компоненты_сборки"
    ADD CONSTRAINT "fk_материнская_плата" FOREIGN KEY ("Материнская плата")
    REFERENCES public."Материнская плата" ("Название");

ALTER TABLE IF EXISTS public."Компоненты_сборки"
    ADD CONSTRAINT "fk_корпус" FOREIGN KEY ("Корпус")
    REFERENCES public."Корпус" ("Название");

ALTER TABLE IF EXISTS public."Компоненты_сборки"
    ADD CONSTRAINT "fk_охлаждение" FOREIGN KEY ("Охлаждение процессора")
    REFERENCES public."Охлаждение процессора" ("Название");

ALTER TABLE IF EXISTS public."Компоненты_сборки"
    ADD CONSTRAINT "fk_оперативная_память" FOREIGN KEY ("Оперативная память")
    REFERENCES public."Оперативная память" ("Название");

ALTER TABLE IF EXISTS public."Компоненты_сборки"
    ADD CONSTRAINT "fk_накопитель" FOREIGN KEY ("Накопитель")
    REFERENCES public."Накопители" ("Название");

ALTER TABLE IF EXISTS public."Компоненты_сборки"
    ADD CONSTRAINT "fk_блок_питания" FOREIGN KEY ("Блок питания")
    REFERENCES public."Блоки_питания" ("Название");

ALTER TABLE IF EXISTS public."Компоненты_сборки"
    ADD CONSTRAINT "fk_доп_детали" FOREIGN KEY ("Доп. детали")
    REFERENCES public."Доп детали" ("Название");

-- Завершение транзакции
END;
