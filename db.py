import sqlite3
import os

def init_db():
    if os.path.exists("shuttle.db"):
        os.remove("shuttle.db")
        print("Removed shuttle_db for fresh start!")



    con = sqlite3.connect("shuttle.db")
    cur = con.cursor()
    cur.execute("PRAGMA foreign_keys = ON")

    cur.execute("CREATE TABLE IF NOT EXISTS trips(trip_id TEXT, start_date TEXT, feed_timestamp INTEGER, schedule_relationship TEXT, route_id TEXT, direction INTEGER, vehicle_id TEXT, PRIMARY KEY (trip_id, start_date, feed_timestamp))")
    cur.execute("CREATE TABLE IF NOT EXISTS stops(t_id TEXT, st_date TEXT, fd_timestamp INTEGER, stop_id TEXT, arrival_time INTEGER, FOREIGN KEY (t_id, st_date, fd_timestamp) REFERENCES trips(trip_id, start_date, feed_timestamp))")

    
    con.commit()
    con.close()

if __name__ == "__main__":
    init_db()