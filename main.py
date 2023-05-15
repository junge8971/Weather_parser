#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import Flask, render_template


app = Flask(__name__)
app.secret_key = 'asfouhvnsldvszkldvmszdfv'


@app.route('/')
def main():

    return render_template('today.html')


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
