from datetime import datetime

from flask import Flask, render_template

from . import app


@app.route("/")
def home():
    return render_template("home.html")

@app.route("/assignment/")
def assignment():
    return render_template("assignment.html")

@app.route("/calendar/")
def calendar():
    return render_template("calendar.html")

@app.route("/api/data")
def get_data():
    return app.send_static_file("data.json")
