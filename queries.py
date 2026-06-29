import sqlite3

# Cancellation rate by route
def cancellation_rate():
    con = sqlite3.connect("shuttle.db")
    conn.row_factory = sqlite3.Row
    pass



def most_stop_updates():
    con = sqlite3.connect("shuttle.db")
    cur = con.cursor()

    query = """
        SELECT
            COUNT(route_id) AS total_stops,
            route_id
        FROM stops
        GROUP BY route_id
        ORDER BY total_stops DESC;
    """
    cur.execute(query)
    results = cur.fetchall()

    print("Top 10 Routes by Stop Updates")
    for row in results[0:10]:
        print(f"Route ID: {row[1]}\twith {row[0]}\tstop updates.")

    trips_query = """
        SELECT
            COUNT(route_id) AS num_trips,
            route_id
        FROM trips
        GROUP BY route_id
        ORDER BY num_trips DESC;
    """

    cur.execute(trips_query)
    trips_results = cur.fetchall()

    print("Top frequency:")
    for row in trips_results:
        print(row)
    
if __name__ == "__main__":
    most_stop_updates()