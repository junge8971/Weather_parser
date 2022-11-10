# Weather_parser

Бэкап базы данных находится в папке bd
База данных работает на сервере postgresSQL

Чтобы делать запрос через модуль Main.py, необходимо
1. Инициализировать класс Datavase
2. Обратится к методу request_to_bd и передать в него строку с текстом запроса
3. Метод вернёт результат обращения к базе данных

Название ячеек таблицы:
        time_UTC DOUBLE PRECISION,
        date DATE,
        wind_direction CHARACTER(20),
        wind_spead CHARACTER(20),
        visibility CHARACTER(50), 
        conditions CHARACTER(50),
        cloudiness CHARACTER(50),
        T DOUBLE PRECISION,
        Td DOUBLE PRECISION,
        f DOUBLE PRECISION,
        Te DOUBLE PRECISION,
        Tes DOUBLE PRECISION,
        Comfort CHARACTER(50),
        P DOUBLE PRECISION,
        Po DOUBLE PRECISION,
        Tmin DOUBLE PRECISION,
        Tmax DOUBLE PRECISION,
        R DOUBLE PRECISION,
        R24 DOUBLE PRECISION,
        S DOUBLE PRECISION,
        id SERIAL PRIMARY KEY
        
Таблицы называются называются по принципу 'y20**',
Период доступных таблиц с 2012 по 2022

