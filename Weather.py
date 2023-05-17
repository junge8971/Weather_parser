#!/usr/bin/env python
# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup
import requests
import psycopg2
from datetime import datetime
from dateutil.relativedelta import relativedelta
from threading import Thread
import time


class WeatherParser:
    def __init__(self):
        self.calendar = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
        self.leap_years = [2024, 2020, 2016, 2012]
        self.current_date = datetime.now()
        self.start_year = 2012
        self.reference_url = 'http://www.pogodaiklimat.ru/weather.php?id=34927&bday={}&fday={}&amonth={}&ayear={}&bot=2'

    def years_iterating(self, start_year: int = 2012,
                        step_fro_iteration: int = 1,
                        start_month: int = 1,
                        start_day: int = 1,
                        end_day: int = None):
        for year in range(start_year, int(self.current_date.year)+1, step_fro_iteration):
            for month in range(start_month, 13):
                if year in self.leap_years and month == 2:
                    current_url = self.reference_url.format(start_day, 29, month, year)
                    self.weather_parsing(current_url, year)
                else:
                    if end_day is not None:
                        current_url = self.reference_url.format(start_day, end_day, month, year)
                        self.weather_parsing(current_url, year)
                    else:
                        current_url = self.reference_url.format(start_day, self.calendar[month - 1], month, year)
                        self.weather_parsing(current_url, year)

    def weather_parsing(self, url: str, year: int):
        time.sleep(20)
        page = requests.get(url)
        print(page)
        page.encoding = 'utf-8'
        page2 = page.text
        soup = BeautifulSoup(page2, 'html.parser')

        archive_table = soup.find('div', {'class': 'archive-table'})
        time_table = archive_table.find('div', {'class': 'archive-table-left-column'}).table
        tr_from_time_table = []
        td_from_time_table = time_table.findAll('td', {'class': 'black'})

        list_for_time = []
        list_for_date = []
        i = 0
        while i < len(td_from_time_table):
            list_for_time.append(td_from_time_table[i].text)
            list_for_date.append(td_from_time_table[i+1].text)
            i += 2

        weather_table = archive_table.find('div', {'class': 'archive-table-wrap'}).table
        tr_from_weather_table = []
        tr_from_weather_table = weather_table.findAll('tr', {'height': '30'})

        insert = Database()
        insert.crating_new_table('y' + str(year))

        counter = 0
        appending_text = []
        for tr in tr_from_weather_table:
            appending_text.append(list_for_time[counter])
            appending_text.append(list_for_date[counter])
            counter += 1
            for td in tr:
                x = str(td).replace('\n', '')
                if x != '':
                    appending_text.append(td.text)

            insert.insert_new_row(self.convert_items_to_float(appending_text, year), 'y'+str(year))
            insert.insert_new_row(self.convert_items_to_float(appending_text, year), 'y2011')
            appending_text = []

    def convert_items_to_float(self, item_list: list, year: int):
        result_list = []
        counter = 0
        while counter < len(item_list):
            if counter == 1:
                counter += 1
                continue
            item = item_list[counter]
            if counter == 0:
                second_item = item_list[1]
                day, month = second_item.split('.')
                item = f'{year}-{month}-{day} {item}:00:00 Europe/Moscow'
                print(item)
            try:
                result_list.append(float('{0:.2f}'.format(item)))
            except ValueError:
                if item == '':
                    item = None
                result_list.append(item)
            counter += 1

        return result_list

    def get_list_of_years_from_bd(self) -> list[str]:
        connect_to_bd = Database()
        created_tables = connect_to_bd.checking_for_tables()

        list_of_years = []
        for item in created_tables:
            list_of_years.append(item[0])
        return list_of_years

    def get_last_received_date_and_time(self, list_of_years: list[str]) -> datetime:
        connect_to_bd = Database()
        list_of_years = self.get_list_of_years_from_bd()

        last_received_day_dirt = connect_to_bd.last_received_day(list_of_years[-1])
        last_received_date = last_received_day_dirt[0][0]
        return last_received_date

    def update_weather_data(self) -> str:
        list_of_years = self.get_list_of_years_from_bd()
        last_received_date = self.get_last_received_date_and_time(list_of_years)
        if last_received_date.date() != self.current_date.date():
            if last_received_date.month == self.current_date.month:
            # delta_time = relativedelta(self.current_date.date(), last_received_date)
                self.years_iterating(start_year=last_received_date.year,
                                     start_month=last_received_date.month,
                                     start_day=last_received_date.day,
                                     end_day=self.current_date.day)
                return 'Update ok'
            else:
                return 'No way to update'
        else:
            return 'No need to update'


class Database:
    def __init__(self):
        self.db_name = 'weather_data'
        self.db_user = 'postgres'
        self.db_password = '123321'
        self.db_host = '127.0.0.1'

    def request_to_bd(self, reqvest_to_db: str, params: list = None):
        try:
            connect = psycopg2.connect(dbname=self.db_name,
                                       user=self.db_user,
                                       password=self.db_password,
                                       host=self.db_host)
            cursor = connect.cursor()
            if params is None:
                cursor.execute(reqvest_to_db)
                connect.commit()
                record = cursor.fetchall()
            else:
                full_reqvest = cursor.mogrify(reqvest_to_db, params)
                cursor.execute(full_reqvest)
                connect.commit()
                record = cursor.fetchall()
            return record
        except Exception as exept:
            print(f'Ошибка подключения: {exept}')
        finally:
            if connect:
                cursor.close()
                connect.close()

    def insert_new_row(self, text_to_insert: list, year: str):
        text = """INSERT INTO {} VALUES
        (
        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 
        %s, %s, %s, %s, %s, %s, %s, %s, %s 
        )""".format(year)
        self.request_to_bd(text, params=text_to_insert)

    def crating_new_table(self, year: str):
        text = """
        CREATE TABLE IF NOT EXISTS {}
        (
        date_and_time_UTC TIMESTAMPTZ PRIMARY KEY,
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
        id SERIAL
        );
        """.format(year)
        return self.request_to_bd(text)

    def checking_for_tables(self) -> list:
        text = """
            SELECT table_name FROM information_schema.tables
            WHERE table_schema NOT IN ('information_schema','pg_catalog')
            ORDER BY table_name;"""
        return self.request_to_bd(text)

    def last_received_day(self, year: str) -> str:
        text = """
        SELECT date_and_time_UTC FROM {} 
        ORDER BY date_and_time_UTC DESC
        limit 1;""".format(year)
        return self.request_to_bd(text)

    def get_weather_json(self, start_date: str, end_date: str) -> list:
        # 2023-1-30 - пример даты
        text = """
        SELECT json_agg(y2011) FROM y2011 
        WHERE
        y2011.date_and_time_utc >= '{}%'::timestamp and y2011.date_and_time_utc <= '{}%'::timestamp;
        """.format(start_date, end_date)
        return self.request_to_bd(text)[0][0]

def main():
    while True:
        command = input('>>> ')
        if command == 'parse':
            a = WeatherParser()
            b = WeatherParser()
            tr1 = Thread(target=a.years_iterating, args=(2012, 2))
            tr2 = Thread(target=b.years_iterating, args=(2013, 2))
            tr1.start()
            tr2.start()
        elif command == 'update':
            a = WeatherParser()
            print(a.update_weather_data())
        elif command == 'custom_pars':
            a = WeatherParser()
            a.years_iterating(start_year=2023, start_month=1)
        else:
            print("""
            parse - спарсить всё
            update - обновить уже имеющиеся данные в перделах текущего месяца
            """)


if __name__ == '__main__':
    main()
