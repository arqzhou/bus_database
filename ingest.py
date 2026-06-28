import json
import sqlite3
import db

def ingest(filepath):
    with open("tripupdates.json", "r") as file:
        data = json.load(file)

    print(type(data))

    trips = data["entity"][0:5]
    print(trips[0])
    trips_data = []

    for trip in trips:
        tripId = trip["tripUpdate"]["trip"]["tripId"]
        startDate = trip["tripUpdate"]["trip"]["startDate"]
        scheduleRelationship = trip["tripUpdate"]["trip"]["scheduleRelationship"]
        routeId = trip["tripUpdate"]["trip"]["routeId"]
        directionId = trip["tripUpdate"]["trip"]["directionId"]
        vehicle = None if scheduleRelationship == "CANCELED" else trip["tripUpdate"]["vehicle"]["id"]
        feedTimestamp = trip["tripUpdate"]["timestamp"]


        # trip_id TEXT, start_date TEXT, feed_timestamp INTEGER, schedule_relationship TEXT, route_id TEXT, direction INTEGER, vehicle_id TEXT, PRIMARY KEY (trip_id, start_date, feed_timestamp))")
        trips_data.append((tripId, startDate, feedTimestamp, scheduleRelationship, routeId, directionId, vehicle))
        print((tripId, startDate, scheduleRelationship, routeId, directionId, vehicle, feedTimestamp))


    con = sqlite3.connect("shuttle.db")
    cur = con.cursor()
    cur.executemany("INSERT INTO trips VALUES (?, ?, ?, ?, ?, ?, ?)", trips_data)
    con.commit()
    con.close()

def check_tables():
    con = sqlite3.connect("shuttle.db")
    cur = con.cursor()

    for row in cur.execute("SELECT trip_id, start_date, feed_timestamp FROM trips ORDER BY feed_timestamp"):
        print(row)
    con.close()
    

if __name__ == "__main__":
    db.init_db()
    ingest("tripupdates.json")
    check_tables()