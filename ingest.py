import json
import sqlite3
import db

def ingest(filepath):
    with open("tripupdates.json", "r") as file:
        data = json.load(file)

    print(type(data))

    trips = data["entity"][0:5]
    print(trips[0])

    for trip in trips:
        tripId = trip["tripUpdate"]["trip"]["tripId"]
        startDate = trip["tripUpdate"]["trip"]["startDate"]
        scheduleRelationship = trip["tripUpdate"]["trip"]["scheduleRelationship"]
        routeId = trip["tripUpdate"]["trip"]["routeId"]
        directionId = trip["tripUpdate"]["trip"]["directionId"]
        vehicle = None if scheduleRelationship == "CANCELED" else trip["tripUpdate"]["vehicle"]["id"]
        feed_timestamp = trip["tripUpdate"]["timestamp"]

        print((tripId, startDate, scheduleRelationship, routeId, directionId, vehicle, feed_timestamp))

if __name__ == "__main__":
    db.init_db()
    ingest("tripupdates.json")