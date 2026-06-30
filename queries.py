import sqlite3
from operator import itemgetter

# Cancellation rate by route
def cancellation_rate():
    con = sqlite3.connect("shuttle.db")
    cur = con.cursor()

    query = """
        SELECT
            route_id,
            COUNT(*) AS total_trips,
            COUNT(CASE WHEN schedule_relationship = 'CANCELED' THEN 1 END) AS canceled_trips,
            ROUND(SUM(CASE WHEN schedule_relationship = 'CANCELED' THEN 1.0 ELSE 0.0 END) / COUNT(*), 2) AS cancel_rate
        FROM trips
        GROUP BY route_id
        ORDER BY cancel_rate DESC;
    """
    cur.execute(query)
    results = cur.fetchall()
    print("There are the 10 Routes with the Highest Cancelation Rate:")
    for result in results[0:10]:
        print(f"Route ID: {result[0]}\twith a cancelation rate of {result[3]}\t. ({result[2]}/{result[1]})")
    con.close()

def most_stop_updates():
    con = sqlite3.connect("shuttle.db")
    cur = con.cursor()

    query = """
        SELECT
            trips.route_id,
            COUNT(*) AS total_stops
        FROM stops
        JOIN trips
            ON stops.t_id = trips.trip_id
                AND stops.st_date = trips.start_date
                AND stops.fd_timestamp = trips.feed_timestamp
        GROUP BY trips.route_id
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

    con.close()

def cancel_trends():
    con = sqlite3.connect("shuttle.db")
    cur = con.cursor()

    query = """
        SELECT
            route_id,
            COUNT(CASE WHEN schedule_relationship = 'CANCELED' THEN 1 END) AS canceled_trips,
            COUNT(*) AS total_trips,
            COUNT(CASE WHEN schedule_relationship = 'CANCELED' AND feed_timestamp = '1782235081' THEN 1 END) AS canceled_earlier_trips,
            COUNT(CASE WHEN feed_timestamp = '1782235081' THEN 1 END) AS total_earlier_trips,
            ROUND(SUM(CASE WHEN schedule_relationship = 'CANCELED' AND feed_timestamp = '1782235081' THEN 1.0 ELSE 0.0 END) / SUM(CASE WHEN feed_timestamp = '1782235081' THEN 1.0 ELSE 0.0 END), 2) AS early_cancel_rate,
            COUNT(CASE WHEN schedule_relationship = 'CANCELED' AND feed_timestamp = '1782835557' THEN 1 END) AS canceled_later_trips,
            COUNT(CASE WHEN feed_timestamp = '1782835557' THEN 1 END) AS total_later_trips,
            ROUND(SUM(CASE WHEN schedule_relationship = 'CANCELED' AND feed_timestamp = '1782835557' THEN 1.0 ELSE 0.0 END) / SUM(CASE WHEN feed_timestamp = '1782835557' THEN 1.0 ELSE 0.0 END), 2) AS late_cancel_rate,
            ROUND(SUM(CASE WHEN schedule_relationship = 'CANCELED' AND feed_timestamp = '1782835557' THEN 1.0 ELSE 0.0 END) / SUM(CASE WHEN feed_timestamp = '1782835557' THEN 1.0 ELSE 0.0 END) - SUM(CASE WHEN schedule_relationship = 'CANCELED' AND feed_timestamp = '1782235081' THEN 1.0 ELSE 0.0 END) / SUM(CASE WHEN feed_timestamp = '1782235081' THEN 1.0 ELSE 0.0 END), 2) AS change_in_rate
        FROM trips
        GROUP BY route_id
        HAVING change_in_rate IS NOT NULL
        ORDER BY change_in_rate DESC;
    """

    cur.execute(query)
    results = cur.fetchall()

    print("Largest Increases in Cancelation Rate:")
    for row in results[0:5]:
        print(f"Route ID: {row[0]}\twith a change of {row[9]}\t(from {row[5]}\tto {row[8]})")

    print("Largest Decreases in Cancelation Rate:")
    for row in results[-1:-6:-1]:
        print(f"Route ID: {row[0]}\twith a change of {row[9]}\t(from {row[5]}\tto {row[8]})")
    
if __name__ == "__main__":
    print("TOTAL STATS:")
    cancellation_rate()
    most_stop_updates()
    print("Historical Trends")
    cancel_trends()