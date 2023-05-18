#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import Flask, render_template

from datetime import datetime, timedelta
import re

import pandas
import pandas as pd
import json
import plotly
import plotly.express as px

from Weather import Database, WeatherParser

app = Flask(__name__)
app.secret_key = 'asfouhvnsldvszkldvmszdfv'


@app.route('/')
def main():
    current_date = datetime.now().date()
    db = Database()
    current_weather = db.get_weather_json(str(current_date), str(current_date + timedelta(days=1)))
    current_weather = make_weather_data_prettily(current_weather)

    data_frame = pd.DataFrame.from_records(current_weather)

    graphs = make_graphs(data_frame)

    return render_template('today.html', weather=current_weather, time=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                           graph_temp=graphs.get('temp'), graph_wind=graphs.get('wind'), graph_wet=graphs.get('wet'))


@app.route('/week')
def week():
    current_date = datetime.now().date()
    current_week_day = current_date.weekday()
    start_date = current_date - timedelta(days=current_week_day)
    db = Database()
    week_weather = db.get_weather_json(str(start_date), str(current_date))
    week_weather = make_weather_data_prettily(week_weather)

    data_frame = pd.DataFrame.from_records(week_weather)

    weather = make_json_with_mean_data(data_frame)

    graphs = make_graphs(data_frame)

    return render_template('period_template.html', period='неделю', weather=weather, time=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                           graph_temp=graphs.get('temp'), graph_wind=graphs.get('wind'), graph_wet=graphs.get('wet'))


@app.route('/month')
def month():
    current_date = datetime.now().date()
    current_day = current_date.day
    start_date = current_date - timedelta(days=current_day)
    db = Database()
    month_weather = db.get_weather_json(str(start_date), str(current_date))

    month_weather = make_weather_data_prettily(month_weather)

    data_frame = pd.DataFrame.from_records(month_weather)

    weather = make_json_with_mean_data(data_frame)

    graphs = make_graphs(data_frame)

    return render_template('period_template.html', period='месяц', weather=weather, time=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                           graph_temp=graphs.get('temp'), graph_wind=graphs.get('wind'), graph_wet=graphs.get('wet'))


def make_weather_data_prettily(data: list[dict]) -> list[dict]:
    for item in data:
        item['date_and_time_utc'] = item['date_and_time_utc'].replace('T', ' ').replace('+03:00', '')
        if item['conditions'] is None:
            item['conditions'] = 'Нет'

        try:
            item['wind_spead'] = float(item['wind_spead'])
        except ValueError:
            item['wind_spead'] = max(re.findall('(\d+)', item['wind_spead']))
    return data


def make_graphs(data_frame: pandas.DataFrame) -> dict[str:str]:
    fig_temp = px.line(data_frame=data_frame, y='t', x='date_and_time_utc',
                       title='График температуры')
    fig_temp.update_layout(xaxis_title="Время", yaxis_title="Температура", )
    graph_temp = json.dumps(fig_temp, cls=plotly.utils.PlotlyJSONEncoder)

    fig_wind = px.line(data_frame=data_frame, y='wind_spead', x='date_and_time_utc',
                       title='График скорости ветра')
    fig_wind.update_layout(xaxis_title="Время", yaxis_title="Скорость ветра, м/с")
    graph_wind = json.dumps(fig_wind, cls=plotly.utils.PlotlyJSONEncoder)

    fig_wet = px.line(data_frame=data_frame, y='f', x='date_and_time_utc',
                      title='График влажности')
    fig_wet.update_layout(xaxis_title="Время", yaxis_title="Влажность воздуха, %")
    graph_wet = json.dumps(fig_wet, cls=plotly.utils.PlotlyJSONEncoder)

    return {'temp': graph_temp, 'wind': graph_wind, 'wet': graph_wet}


def make_json_with_mean_data(data_frame: pandas.DataFrame) -> dict:
    t = data_frame['t'].mean()
    f = data_frame['f'].mean()
    wind_direction = data_frame['wind_direction'].value_counts().index[0]
    data_frame['wind_spead'] = pd.to_numeric(data_frame['wind_spead'], downcast='float')
    wind_spead = data_frame['wind_spead'].mean()
    cloudiness = data_frame['cloudiness'].value_counts().index[0]
    comfort = data_frame['comfort'].value_counts().index[0]
    conditions = data_frame['conditions'].value_counts().index[0]
    weather = {
        't': int(t),
        'f': int(f),
        'wind_direction': wind_direction,
        'wind_spead': int(wind_spead),
        'cloudiness': cloudiness,
        'comfort': comfort,
        'conditions': conditions,
    }
    return weather


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
