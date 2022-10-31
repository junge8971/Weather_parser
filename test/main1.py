#!/usr/bin/env python
# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup
import requests
import pathlib as pl
import json
import pandas as pd


def main():
    a = WeatherParser()


class WeatherParser:
    def __init__(self):
        self.calendar = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
        self.leap_years = [24, 20, 16, 12]
        self.column_names = ['Ветер напр.', 'Ветер, м/с', 'Видим.', 'Явления',
                             'Облачность', 'Т(С)', 'Тd(С)', 'f(%)', 'Тe(С)', 'Тes(С)',
                             'Комфортность', 'P(гПа)', 'Po(гПа)', 'Тmin(С)', 'Tmax(С), R(мм)',
                             'R24(мм)', 'S(см)']
        self.reference_url = 'http://www.pogodaiklimat.ru/weather.php?id=34927&bday=1&fday={}&amonth={}&ayear={}&bot=2'
        self.file_name = 'weather_result.json'

        self.years_iterating()

    def years_iterating(self):
        if not pl.Path(self.file_name).exists():
            creating_file = pl.Path.cwd() / self.file_name
            pl.Path.touch(creating_file)

        for year in range(12, 13): # 23
            for month in range(1, 2): #13
                if year in self.leap_years and month == 2:
                    curren_url = self.reference_url.format(29, month, '20'+str(year))
                    self.weather_parsing(curren_url, year, month)
                else:
                    curren_url = self.reference_url.format(self.calendar[month-1], month, '20'+str(year))
                    self.weather_parsing(curren_url, year, month)

    def weather_parsing(self, url, year, month):
        with open(self.file_name, 'r', encoding='utf-8') as file:
            weather_result_all = json.load(file)
            current_year = weather_result_all.get(str(year))

        if current_year:
            current_month = current_year.get(str(month))

            if current_month:
                page = requests.get(url)
                soup = BeautifulSoup(page.text, 'html.parser')
                trs = []
                trs = soup.findAll('tr', height="30")

                data_frame = []
                for tr in trs:
                    appending_data = []
                    td_counter = 0
                    for td in tr:
                        x = str(td).replace('\n', '')
                        if x == '':
                            continue
                        else:
                            try:
                                appending_data.append({self.column_names[td_counter]: td.text})
                                td_counter += 1
                                print(appending_data)
                            except IndexError:
                                pass

                    data_frame.append(appending_data)
                print(data_frame)

    def month_weather_date_plus_data(self, data):
        pass



if __name__ == '__main__':
    main()
