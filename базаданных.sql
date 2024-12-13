BEGIN;

CREATE TABLE IF NOT EXISTS public."Компоненты_сборки"
(
    id serial NOT NULL,
    "id_сборки" integer NOT NULL,
    "id_компонента" integer NOT NULL,
    "Количество" integer DEFAULT 1,
    CONSTRAINT pk_компоненты_сборки PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS public."Сборки"
(
    id serial NOT NULL,
    "Название_сборки" character varying(255) NOT NULL,
    "Общая_цена" numeric(10, 2) NOT NULL,
    "id_пользователя" integer NOT NULL,
    "Статус_сборки" character varying(50) NOT NULL,
    "Дата_создания" timestamp DEFAULT CURRENT_TIMESTAMP,
    "Дата_завершения" timestamp,
    CONSTRAINT pk_сборки PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS public."Компоненты"
(
    id serial NOT NULL,
    "Категория" character varying(255) NOT NULL,
    "Название" character varying(255) NOT NULL,
    "Цена" numeric(10, 2) NOT NULL,
    "Описание" text,
    CONSTRAINT pk_компоненты PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS public."Пользователи"
(
    id serial NOT NULL,
    "Никнейм" character varying(255) NOT NULL,
    "Пароль" character varying(255) NOT NULL,
    CONSTRAINT pk_пользователи PRIMARY KEY (id),
    CONSTRAINT уникальный_никнейм UNIQUE ("Никнейм")
);

ALTER TABLE IF EXISTS public."Компоненты_сборки"
    ADD CONSTRAINT fk_сборка FOREIGN KEY ("id_сборки")
    REFERENCES public."Сборки" (id)
    ON UPDATE NO ACTION
    ON DELETE CASCADE;

ALTER TABLE IF EXISTS public."Компоненты_сборки"
    ADD CONSTRAINT fk_компонент FOREIGN KEY ("id_компонента")
    REFERENCES public."Компоненты" (id)
    ON UPDATE NO ACTION
    ON DELETE CASCADE;

ALTER TABLE IF EXISTS public."Сборки"
    ADD CONSTRAINT fk_пользователь FOREIGN KEY ("id_пользователя")
    REFERENCES public."Пользователи" (id)
    ON UPDATE NO ACTION
    ON DELETE CASCADE;

END;