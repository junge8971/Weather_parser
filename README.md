# Weather_parser

Бэкап базы данных находится в папке bd
База данных работает на сервере postgresSQL

Чтобы делать запрос через модуль Main.py, необходимо
1. Инициализировать класс Datavase
2. Обратится к методу request_to_bd и передать в него строку с текстом запроса
3. Метод вернёт результат обращения к базе данных

Название ячеек таблицы:
        time_UTC CHARACTER(15),
        date CHARACTER(15),
        wind_direction CHARACTER(10),
        wind_spead CHARACTER(15),
        visibility CHARACTER(50), 
        conditions CHARACTER(50),
        cloudiness CHARACTER(50),
        T CHARACTER(15),
        Td CHARACTER(15),
        f CHARACTER(15),
        Te CHARACTER(15),
        Tes CHARACTER(15),
        Comfort CHARACTER(50),
        P CHARACTER(15),
        Po CHARACTER(15),
        Tmin CHARACTER(15),
        Tmax CHARACTER(15),
        R CHARACTER(15),
        R24 CHARACTER(15),
        S CHARACTER(15),
        id SERIAL PRIMARY KEY
        
Таблицы называются называются по принципу 'y20**',
Период доступных таблиц с 2012 по 2022

