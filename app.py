import numpy as np
import pandas as pd

import datetime as dt
from datetime import timedelta, date

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify, render_template


engine = create_engine("sqlite:///Resources/hawaii.sqlite")
Base = automap_base()
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station


# Flask Setup
app = Flask(__name__)


@app.route("/")
def welcome():
    return (
        f'Welcome to Hawaii Weather Service!<br/>'
        f'Available Routes:<br/>'
        f'-----------------------------<br/v>'
        f'/api/v1.0/precipitation<br/>'
        f'/api/v1.0/stations<br/>'
        f'/api/v1.0/tobs<br/>'
        f'/api/v1.0/start_date<br/>'
        f'----Format: /api/v1.0/yyyy-mm-dd<br/>'
        f'----Example: /api/v1.0/2000-01-01<br/>'
        f'/api/v1.0/start_date/end_date<br/>'
        f'----Format: /api/v1.0/yyyy-mm-dd/yyyy-mm-dd<br/>'
        f'----Example: /api/v1.0/2010-01-01/2010-01-10<br/>'
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)

    date = dt.date(2017, 8, 23) - dt.timedelta(days=366)

    precip_last_twelve = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date > date).order_by(Measurement.date).all()

    session.close()

    all_precip = []
    for date, prcp in precip_last_twelve:
        precip_dict = {}
        precip_dict['date'] = date
        precip_dict['precipitation'] = prcp
        all_precip.append(precip_dict)

    return jsonify(all_precip)

@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)

    stations = session.query(Measurement.station, func.count(Measurement.station)).group_by(Measurement.station).all()

    session.close()

    all_stations = []
    for station, count in stations:
        stations_dict = {}
        stations_dict['station'] = station
        stations_dict['count'] = count
        all_stations.append(stations_dict)

    return jsonify(all_stations)


@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)

    date = dt.date(2017, 8, 23) - dt.timedelta(days=366)
    temp_obs = session.query(Measurement.date, Measurement.tobs).filter(Measurement.station == 'USC00519281').filter(Measurement.date >= date).all()
    
    session.close()

    all_tobs = []
    for date, temp in temp_obs:
        tobs_dict = {}
        tobs_dict['station'] = date
        tobs_dict['count'] = temp
        all_tobs.append(tobs_dict)

    return jsonify(all_tobs)

@app.route("/api/v1.0/<start>")
def start_rt(start):
    
    session = Session(engine)

    date = dt.date(*(int(s) for s in start.split('-')))

    start_query = session.query(Measurement.station, func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).filter(Measurement.date >= date).group_by(Measurement.station).all()

    session.close()

    all_start = []
    for station, min, max, avg in start_query:
        start_dict = {}
        start_dict['station'] = station
        start_dict['min temp'] = min
        start_dict['max temp'] = max
        start_dict['avg temp'] = avg
        all_start.append(start_dict)

    if date >= dt.date(2010, 1, 1) and date <= dt.date(2017, 8, 23):
        return jsonify(all_start)
    else:
        return jsonify({"error": "Date input incorrectly or does not exist in dataset."}), 404

@app.route("/api/v1.0/<start>/<end>")
def end(start, end):
    session = Session(engine)

    date_start = dt.date(*(int(s) for s in start.split('-')))
    date_end = dt.date(*(int(s) for s in end.split('-')))

    end_query = session.query(Measurement.station, func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).filter(Measurement.date >= date_start).filter(Measurement.date <= date_end).group_by(Measurement.station).all()

    session.close()

    all_end = []
    for station, min, max, avg in end_query:
        end_dict = {}
        end_dict['station'] = station
        end_dict['min temp'] = min
        end_dict['max temp'] = max
        end_dict['avg temp'] = avg
        all_end.append(end_dict)

    if date_start >= dt.date(2010, 1, 1) and date_end <= dt.date(2017, 8, 23) and date_start < date_end:
        return jsonify(all_end)
    else:
        return jsonify({"error": "Date input incorrectly or does not exist in dataset."}), 404

@app.errorhandler(ValueError)
def input_incorrectly(e):
    # note that we set the 404 status explicitly
    return jsonify({"error": f"Date input incorrectly or does not exist in dataset."}), 404

if __name__ == "__main__":
    app.run(debug=True)
