# Import 

import numpy as np
import pandas as pd 
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine , func

# import flask
from flask import Flask, jsonify

#Create engine to hawaii.sqlite
engine = create_engine("sqlite:///Resources/hawaii.sqlite",connect_args={'check_same_thread': False})
#reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect = True)

#View all of the classes that automap found
Base.classes.keys()

#Save refernces to each table 
measurement = Base.classes.measurement
station = Base.classes.station

#create our session(link) from Python to the DB
session = Session(engine)

app = Flask(__name__)

@app.route("/")
def  welcome():
    """List all available api routes."""
    return (
        f"Welcome to Hawaii Climate API! <br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/&lt;start&gt;<br>"
        f"/api/v1.0/&lt;start&gt;/&lt;end&gt;<br>"
    )

@app.route("/api/v1.0/preciptation")
def precipitation_route():
     # Create our session (link) from Python to the DB
    

    # Find the most recent date in the data set.
    recent_date = session.query(measurement.date).order_by(measurement.date.desc()).first()

    # Calculate the date one year from the last date in data set.
    last_year_date = dt.date(2017,8,23)- dt.timedelta(days= 364)

    # formating the date 
    lastyear_startdate = (dt.datetime.strptime(recent_date[0],'%Y-%m-%d') - dt.timedelta(days=364)).strftime('%Y-%m-%d')

    # Perform a query to retrieve the data and precipitation scores
    most_recent_prec = session.query(measurement.date,measurement.prcp).filter(measurement.date >= lastyear_startdate).all()

    
    ## Convert list of tuples into normal list
    # all_precip = list(np.ravel(most_recent_prec))
    all_precip = {result[0]:result[1] for result in most_recent_prec}

    return jsonify(all_precip)


@app.route("/api/v1.0/stations")
def stations():
    results = session.query(station.station).all()

    stations = list(np.ravel(results))

    return jsonify(stations)    


@app.route("/api/v1.0/tobs")
def tobs():
    prev_year = dt.date(2017,8,23)-dt.timedelta(days = 365)

    # Query the primary station for all tobs from the last year
    results = session.query(measurement.tobs).\
        filter(measurement.station == 'USC00519281').\
        filter(measurement.date >= prev_year).all()
    
    temps = list(np.ravel(results))

    return jsonify (temps)


@app.route("/api/v1.0/<start>")
@app.route("/api/v1.0/<start>/<end>")
def stats(start, end = None):
    if not end:
        results = session.query(measurement.date, func.min(measurement.tobs),func.avg(measurement.tobs),func.max(measurement.tobs)).\
            filter(measurement.date >= start).all()
    else:
        results = session.query(measurement.date, func.min(measurement.tobs),func.avg(measurement.tobs),func.max(measurement.tobs)).\
            filter(measurement.date >= start).filter(measurement.date < end).all()
    
    final_results = list(np.ravel(results))

    return jsonify(temps = final_results)







if __name__ == '__main__':
    app.run(debug=True)