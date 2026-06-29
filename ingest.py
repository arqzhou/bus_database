import json
import sqlite3
import db

def ingest(filepath):
    with open(filepath, "r") as file:
        data = json.load(file)

    trips = data["entity"]
    feedTimestamp = data["header"]["timestamp"]
    trips_data = []
    stop_data = []

    for trip in trips:
        tripId = trip["tripUpdate"]["trip"]["tripId"]
        startDate = trip["tripUpdate"]["trip"]["startDate"]
        scheduleRelationship = trip["tripUpdate"]["trip"]["scheduleRelationship"]
        routeId = trip["tripUpdate"]["trip"]["routeId"]
        directionId = trip["tripUpdate"]["trip"]["directionId"]
        if scheduleRelationship == "CANCELED" or "vehicle" not in trip["tripUpdate"]:
            vehicle = None
        else:
            vehicle = trip["tripUpdate"]["vehicle"]["id"]
        
        # trip_id TEXT, start_date TEXT, feed_timestamp INTEGER, schedule_relationship TEXT, route_id TEXT, direction INTEGER, vehicle_id TEXT, PRIMARY KEY (trip_id, start_date, feed_timestamp))")
        trips_data.append((tripId, startDate, feedTimestamp, scheduleRelationship, routeId, directionId, vehicle))

        if scheduleRelationship == "SCHEDULED":
            stops = trip["tripUpdate"]["stopTimeUpdate"]
            for stop in stops:
                if "arrival" in stop:
                    stopId = stop["stopId"]
                    arrivalTime = stop["arrival"]["time"]
                    #t_id TEXT, st_date TEXT, fd_timestamp INTEGER, stop_id TEXT, arrival_time INTEGER
                    stop_data.append((tripId, startDate, feedTimestamp, stopId, arrivalTime))
                

    con = sqlite3.connect("shuttle.db")
    cur = con.cursor()
    cur.executemany("INSERT INTO trips (trip_id, start_date, feed_timestamp, schedule_relationship, route_id, direction, vehicle_id) VALUES (?, ?, ?, ?, ?, ?, ?)", trips_data)
    cur.executemany("INSERT INTO stops (t_id, st_date, fd_timestamp, stop_id, arrival_time) VALUES (?, ?, ?, ?, ?)", stop_data)
        
    con.commit()
    con.close()

def check_tables():
    con = sqlite3.connect("shuttle.db")
    cur = con.cursor()

    for row in cur.execute("SELECT trip_id, start_date, feed_timestamp, vehicle_id FROM trips ORDER BY feed_timestamp"):
        print(row)

    for row in cur.execute("SELECT t_id, st_date, fd_timestamp, stop_id, arrival_time FROM stops ORDER BY fd_timestamp"):
        print(row)
    con.close()
    

if __name__ == "__main__":
    db.init_db()
    ingest("tripupdates.json")
