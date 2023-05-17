#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import Flask, render_template

from datetime import datetime, timedelta
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

    for item in current_weather:
        item['date_and_time_utc'] = item['date_and_time_utc'].replace('T', ' ').replace('+03:00', '')
        if item['conditions'] is None:
            item['conditions'] = 'Нет'

    data_frame = pd.DataFrame.from_records(current_weather)

    fig_temp = px.line(data_frame=data_frame, y='t', x='date_and_time_utc',
                       title='График температуры за сегодня')
    fig_temp.update_layout(xaxis_title="Время", yaxis_title="Температура",)
    graph_temp = json.dumps(fig_temp, cls=plotly.utils.PlotlyJSONEncoder)

    fig_wind = px.line(data_frame=data_frame, y='wind_spead', x='date_and_time_utc',
                       title='График скорости ветра за сегодня')
    fig_wind.update_layout(xaxis_title="Время", yaxis_title="Скорость ветра, м/с")
    graph_wind = json.dumps(fig_wind, cls=plotly.utils.PlotlyJSONEncoder)

    fig_wet = px.line(data_frame=data_frame, y='f', x='date_and_time_utc',
                       title='График влажности за сегодня')
    fig_wet.update_layout(xaxis_title="Время", yaxis_title="Влажность воздуха, %")
    graph_wet = json.dumps(fig_wet, cls=plotly.utils.PlotlyJSONEncoder)

    return render_template('today.html', weather=current_weather, time=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                           graph_temp=graph_temp, graph_wind=graph_wind, graph_wet=graph_wet)


if __name__ == '__main__':
    update = WeatherParser()
    update.update_weather_data()
    app.run(host='0.0.0.0', debug=True)
