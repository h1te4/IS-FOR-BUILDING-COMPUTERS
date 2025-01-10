BEGIN;

-- Таблица для пользователей
CREATE TABLE IF NOT EXISTS public."Пользователи" (
    "id_Пользователя" serial PRIMARY KEY,
    "Никнейм" character varying(255) UNIQUE NOT NULL,
    "Пароль" character varying(255) NOT NULL,
    "Дата_регистрации" date
);

-- Общая таблица для компонентов
CREATE TABLE IF NOT EXISTS public."Компоненты" (
    "id_Компонента" serial PRIMARY KEY,
    "Категория" character varying(255) NOT NULL, -- Процессор, Видеокарта, и т.д.
    "Название" character varying(255) NOT NULL,
    "Описание" text,
    "Цена" numeric(8, 2) NOT NULL
);

-- Таблица для сборок
CREATE TABLE IF NOT EXISTS public."Сборки" (
    "id_сборки" serial PRIMARY KEY,
    "Название_сборки" character varying(255) NOT NULL,
    "Общая_цена" numeric(10, 2) NOT NULL,
    "id_Пользователя" integer NOT NULL,
    "Статус_сборки" character varying(50) NOT NULL,
    "Дата_создания" timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    "Дата_завершения" timestamp without time zone,
    CONSTRAINT "fk_пользователь" FOREIGN KEY ("id_Пользователя")
        REFERENCES public."Пользователи" ("id_Пользователя") ON DELETE CASCADE
);

-- Промежуточная таблица для связи сборок и компонентов
CREATE TABLE IF NOT EXISTS public."Сборка_Компоненты" (
    "id_сборки" integer NOT NULL,
    "id_компонента" integer NOT NULL,
    CONSTRAINT "fk_сборка" FOREIGN KEY ("id_сборки")
        REFERENCES public."Сборки" ("id_сборки") ON DELETE CASCADE,
    CONSTRAINT "fk_компонент" FOREIGN KEY ("id_компонента")
        REFERENCES public."Компоненты" ("id_Компонента") ON DELETE CASCADE,
    PRIMARY KEY ("id_сборки", "id_компонента")
);

-- Таблица для дополнительных свойств компонентов (например, сокет у процессоров)
CREATE TABLE IF NOT EXISTS public."Свойства_Компонентов" (
    "id_Компонента" integer NOT NULL,
    "Свойство" character varying(255) NOT NULL,
    "Значение" character varying(255) NOT NULL,
    CONSTRAINT "fk_компонент_свойство" FOREIGN KEY ("id_Компонента")
        REFERENCES public."Компоненты" ("id_Компонента") ON DELETE CASCADE
);

END;
