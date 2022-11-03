#!/usr/bin/env python
# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup
import requests
import psycopg2
from datetime import datetime
from threading import Thread


def main():
    a = WeatherParser()
    TR1 = Thread(target=a.years_iterating, args=(2012, 2))
    TR2 = Thread(target=a.years_iterating, args=(2013, 2))
    TR1.start()
    TR2.start()


class WeatherParser:
    def __init__(self):
        self.calendar = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
        self.leap_years = [2024, 2020, 2016, 2012]
        self.current_date = datetime.now()
        self.reference_url = 'http://www.pogodaiklimat.ru/weather.php?id=34927&bday=1&fday={}&amonth={}&ayear={}&bot=2'

    def years_iterating(self, start_year=2012, step_fro_iteration=1):
        for year in range(start_year, int(self.current_date.year)+1, step_fro_iteration):
            for month in range(1, 13):
                if year in self.leap_years and month == 2:
                    current_url = self.reference_url.format(29, month, year)
                    self.weather_parsing(current_url, year)
                else:
                    current_url = self.reference_url.format(self.calendar[month - 1], month, year)
                    self.weather_parsing(current_url, year)

    def weather_parsing(self, url, year):
        page = requests.get(url)
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
            insert.insert_new_row(self.convert_items_to_float(appending_text, year), year)
            appending_text = []

    # to do: в поле с датой в 10-ом месяце пропадает ноль
    def convert_items_to_float(self, item_list, year):
        result_list = []
        counter = 0
        while counter < len(item_list):
            item = item_list[counter]
            if counter == 1:
                day, mounth = item.split('.')
                item = f'{year}-{mounth}-{day}'
            try:
                result_list.append(float('{0:.2f}'.format(item)))
            except ValueError:
                if item == '':
                    item = None
                result_list.append(item)
            counter += 1

        print(result_list)
        return result_list


class Database:
    def __init__(self):
        self.db_name = 'weather_data'
        self.db_user = 'postgres'
        self.db_password = '123321'
        self.db_host = '127.0.0.1'

    def request_to_bd(self, reqvest_to_db, params=None):
        try:
            connect = psycopg2.connect(dbname=self.db_name,
                                       user=self.db_user,
                                       password=self.db_password,
                                       host=self.db_host)
            cursor = connect.cursor()
            if params is None:
                cursor.execute(reqvest_to_db)
                connect.commit()
                record = cursor.fetchone()
            else:
                full_reqvest = cursor.mogrify(reqvest_to_db, params)
                cursor.execute(full_reqvest)
                connect.commit()
                record = cursor.fetchone()
            return record
        except Exception as exept:
            print(f'Ошибка подключения: {exept}')
        finally:
            if connect:
                cursor.close()
                connect.close()
                print('База данных закрыта')

    def insert_new_row(self, text_to_insert, year):
        current_year = 'y'+str(year)
        text = """INSERT INTO {} VALUES
        (
        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 
        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s 
        )""".format(current_year)
        self.request_to_bd(text, params=text_to_insert)

    def crating_new_table(self, year):
        text = """
        CREATE TABLE IF NOT EXISTS {}
        (
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
        );
        """.format(year)
        return self.request_to_bd(text)

    
if __name__ == '__main__':
    main()
