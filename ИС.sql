-- This script was generated by the ERD tool in pgAdmin 4.
-- Please log an issue at https://github.com/pgadmin-org/pgadmin4/issues/new/choose if you find any bugs, including reproduction steps.
BEGIN;


CREATE TABLE IF NOT EXISTS public."Блоки_питания"
(
    "Название" character varying(255) COLLATE pg_catalog."default" NOT NULL,
    "Мощность" integer NOT NULL,
    "Описание" text COLLATE pg_catalog."default" NOT NULL,
    "Цена" numeric(8, 2) NOT NULL,
    CONSTRAINT "Блоки_питания_pkey" PRIMARY KEY ("Название")
);

CREATE TABLE IF NOT EXISTS public."Видеокарты"
(
    "Название" character varying(255) COLLATE pg_catalog."default" NOT NULL,
    "Описание" text COLLATE pg_catalog."default" NOT NULL,
    "Цена" numeric(8, 2) NOT NULL,
    CONSTRAINT "Видеокарты_pkey" PRIMARY KEY ("Название")
);

CREATE TABLE IF NOT EXISTS public."Доп детали"
(
    "Название" character varying(255) COLLATE pg_catalog."default" NOT NULL,
    "Описание" text COLLATE pg_catalog."default" NOT NULL,
    "Цена" numeric(8, 2) NOT NULL,
    CONSTRAINT "Доп детали_pkey" PRIMARY KEY ("Название")
);

CREATE TABLE IF NOT EXISTS public."Компоненты_сборки"
(
    id serial NOT NULL,
    "id_сборки" integer NOT NULL,
    "Процессор" character varying(255) COLLATE pg_catalog."default",
    "Видеокарта" character varying(255) COLLATE pg_catalog."default",
    "Материнская плата" character varying(255) COLLATE pg_catalog."default",
    "Корпус" character varying(255) COLLATE pg_catalog."default",
    "Охлаждение процессора" character varying(255) COLLATE pg_catalog."default",
    "Оперативная память" character varying(255) COLLATE pg_catalog."default",
    "Накопитель" character varying(255) COLLATE pg_catalog."default",
    "Блок питания" character varying(255) COLLATE pg_catalog."default",
    "Доп. детали" character varying(255) COLLATE pg_catalog."default",
    CONSTRAINT "pk_компоненты_сборки" PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS public."Корпус"
(
    "Название" character varying(255) COLLATE pg_catalog."default" NOT NULL,
    "Описание" text COLLATE pg_catalog."default" NOT NULL,
    "Цена" numeric(8, 2) NOT NULL,
    CONSTRAINT "Корпус_pkey" PRIMARY KEY ("Название")
);

CREATE TABLE IF NOT EXISTS public."Материнская плата"
(
    "Название" character varying(255) COLLATE pg_catalog."default" NOT NULL,
    "Сокет" character varying(100) COLLATE pg_catalog."default" NOT NULL,
    "Описание" text COLLATE pg_catalog."default" NOT NULL,
    "Цена" numeric(8, 2) NOT NULL,
    CONSTRAINT "Материнская плата_pkey" PRIMARY KEY ("Название")
);

CREATE TABLE IF NOT EXISTS public."Накопители"
(
    "Название" character varying(255) COLLATE pg_catalog."default" NOT NULL,
    "Объём" character varying(100) COLLATE pg_catalog."default" NOT NULL,
    "Описание" text COLLATE pg_catalog."default" NOT NULL,
    "Цена" numeric(8, 2) NOT NULL,
    CONSTRAINT "Накопители_pkey" PRIMARY KEY ("Название")
);

CREATE TABLE IF NOT EXISTS public."Оперативная память"
(
    "Название" character varying(255) COLLATE pg_catalog."default" NOT NULL,
    "Описание" text COLLATE pg_catalog."default" NOT NULL,
    "Цена" numeric(8, 2) NOT NULL,
    CONSTRAINT "Оперативная память_pkey" PRIMARY KEY ("Название")
);

CREATE TABLE IF NOT EXISTS public."Охлаждение процессора"
(
    "Название" character varying(255) COLLATE pg_catalog."default" NOT NULL,
    "Описание" text COLLATE pg_catalog."default" NOT NULL,
    "Цена" numeric(8, 2) NOT NULL,
    CONSTRAINT "Охлаждение процессора_pkey" PRIMARY KEY ("Название")
);

CREATE TABLE IF NOT EXISTS public."Пользователи"
(
    "id_Пользователя" integer NOT NULL DEFAULT nextval('"Пользователи_id_seq"'::regclass),
    "Никнейм" character varying(255) COLLATE pg_catalog."default" NOT NULL,
    "Пароль" character varying(255) COLLATE pg_catalog."default" NOT NULL,
    "Дата_регистрации" date,
    CONSTRAINT "pk_пользователи" PRIMARY KEY ("id_Пользователя")
);

CREATE TABLE IF NOT EXISTS public."Процессоры"
(
    "Название" character varying(255) COLLATE pg_catalog."default" NOT NULL,
    "Описание" text COLLATE pg_catalog."default" NOT NULL,
    "Сокет" character varying(100) COLLATE pg_catalog."default" NOT NULL,
    "Цена" numeric(8, 2) NOT NULL,
    CONSTRAINT "Процессоры_pkey" PRIMARY KEY ("Название")
);

CREATE TABLE IF NOT EXISTS public."Сборки"
(
    "id_сборки" serial NOT NULL,
    "Название_сборки" character varying(255) COLLATE pg_catalog."default" NOT NULL,
    "Общая_цена" numeric(10, 2) NOT NULL,
    "id_Пользователя" integer NOT NULL,
    "Статус_сборки" character varying(50) COLLATE pg_catalog."default" NOT NULL,
    "Дата_создания" timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    "Дата_завершения" timestamp without time zone,
    CONSTRAINT "pk_сборки" PRIMARY KEY ("id_сборки")
);

ALTER TABLE IF EXISTS public."Компоненты_сборки"
    ADD CONSTRAINT "fk_блок_питания" FOREIGN KEY ("Блок питания")
    REFERENCES public."Блоки_питания" ("Название") MATCH SIMPLE
    ON UPDATE NO ACTION
    ON DELETE NO ACTION;


ALTER TABLE IF EXISTS public."Компоненты_сборки"
    ADD CONSTRAINT "fk_видеокарта" FOREIGN KEY ("Видеокарта")
    REFERENCES public."Видеокарты" ("Название") MATCH SIMPLE
    ON UPDATE NO ACTION
    ON DELETE NO ACTION;


ALTER TABLE IF EXISTS public."Компоненты_сборки"
    ADD CONSTRAINT "fk_доп_детали" FOREIGN KEY ("Доп. детали")
    REFERENCES public."Доп детали" ("Название") MATCH SIMPLE
    ON UPDATE NO ACTION
    ON DELETE NO ACTION;


ALTER TABLE IF EXISTS public."Компоненты_сборки"
    ADD CONSTRAINT "fk_корпус" FOREIGN KEY ("Корпус")
    REFERENCES public."Корпус" ("Название") MATCH SIMPLE
    ON UPDATE NO ACTION
    ON DELETE NO ACTION;


ALTER TABLE IF EXISTS public."Компоненты_сборки"
    ADD CONSTRAINT "fk_материнская_плата" FOREIGN KEY ("Материнская плата")
    REFERENCES public."Материнская плата" ("Название") MATCH SIMPLE
    ON UPDATE NO ACTION
    ON DELETE NO ACTION;


ALTER TABLE IF EXISTS public."Компоненты_сборки"
    ADD CONSTRAINT "fk_накопитель" FOREIGN KEY ("Накопитель")
    REFERENCES public."Накопители" ("Название") MATCH SIMPLE
    ON UPDATE NO ACTION
    ON DELETE NO ACTION;


ALTER TABLE IF EXISTS public."Компоненты_сборки"
    ADD CONSTRAINT "fk_оперативная_память" FOREIGN KEY ("Оперативная память")
    REFERENCES public."Оперативная память" ("Название") MATCH SIMPLE
    ON UPDATE NO ACTION
    ON DELETE NO ACTION;


ALTER TABLE IF EXISTS public."Компоненты_сборки"
    ADD CONSTRAINT "fk_охлаждение" FOREIGN KEY ("Охлаждение процессора")
    REFERENCES public."Охлаждение процессора" ("Название") MATCH SIMPLE
    ON UPDATE NO ACTION
    ON DELETE NO ACTION;


ALTER TABLE IF EXISTS public."Компоненты_сборки"
    ADD CONSTRAINT "fk_процессор" FOREIGN KEY ("Процессор")
    REFERENCES public."Процессоры" ("Название") MATCH SIMPLE
    ON UPDATE NO ACTION
    ON DELETE NO ACTION;


ALTER TABLE IF EXISTS public."Компоненты_сборки"
    ADD CONSTRAINT "fk_сборка" FOREIGN KEY ("id_сборки")
    REFERENCES public."Сборки" ("id_сборки") MATCH SIMPLE
    ON UPDATE NO ACTION
    ON DELETE CASCADE;


ALTER TABLE IF EXISTS public."Сборки"
    ADD CONSTRAINT "fk_пользователь" FOREIGN KEY ("id_Пользователя")
    REFERENCES public."Пользователи" ("id_Пользователя") MATCH SIMPLE
    ON UPDATE NO ACTION
    ON DELETE CASCADE;

END;