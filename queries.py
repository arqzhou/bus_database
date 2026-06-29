import sqlite3
from operator import itemgetter

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
            route_id,
            COUNT(route_id) AS total_stops
        FROM stops
        GROUP BY route_id
        ORDER BY total_stops DESC;
    """
    cur.execute(query)
    results = cur.fetchall()

    print("Top 10 Routes by Stop Updates")
    for row in results[0:10]:
        print(f"Route ID: {row[0]}\twith {row[1]}\tstop updates.")

    trips_query = """
        SELECT
            route_id,
            COUNT(route_id) AS num_trips
        FROM trips
        GROUP BY route_id
        ORDER BY num_trips DESC;
    """

    cur.execute(trips_query)
    trips_results = cur.fetchall()

    print("Top 10 Routes by Route Frequency:")
    for row in trips_results[0:10]:
        print(f"Route ID: {row[0]}\trecorded {row[1]}\ttrips.")

    results_dict = dict(results)
    trips_results_dict = dict(trips_results)

    avg_results = []
    for key in results_dict:
        avg_results.append((key, round(results_dict[key]/trips_results_dict[key], 2)))
    sorted_avg_results = sorted(avg_results, key=itemgetter(1), reverse = True)

    print("Top 10 Busiest Routes (by stop update average):")
    for row in sorted_avg_results[0:10]:
        print(f"Route ID: {row[0]}\t has {row[1]}\t stop updates, on average.")
    
if __name__ == "__main__":
    most_stop_updates()