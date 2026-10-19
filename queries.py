import sqlite3
from operator import itemgetter
from matplotlib import pyplot as plt

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
    print("These are the 10 Routes with the Highest Cancelation Rate:")
    route_ids = []
    cancel_rates = []
    for result in results[0:10]:
        route_ids.append(result[0])
        cancel_rates.append(result[3])
        print(f"Route ID: {result[0]}\twith a cancelation rate of {result[3]}\t. ({result[2]}/{result[1]})")

    plt.figure(1)
    plt.bar(route_ids, cancel_rates)
    plt.title("Top 10 Routes by Cancelation Rate")
    plt.xlabel("Route ID")
    plt.ylabel("Cancel Rate")

    print(results[0:10][0])
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
    route_ids = []
    stop_updates = []

    print("Top 10 Routes by Stop Updates")
    for result in results[0:10]:
        route_ids.append(result[0])
        stop_updates.append(result[1])
        print(f"Route ID: {result[0]}\twith {result[1]}\tstop updates.")

    plt.figure(2)
    plt.bar(route_ids, stop_updates)
    plt.title("Top 10 Routes by Stop Updates")
    plt.xlabel("Route ID")
    plt.ylabel("Stop Updates")


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

    route_ids = []
    trip_freqs = []
    print("Top 10 Routes by Route Frequency:")
    for row in trips_results[0:10]:
        route_ids.append(row[0])
        trip_freqs.append(row[1])
        print(f"Route ID: {row[0]}\trecorded {row[1]}\ttrips.")

    plt.figure(3)
    plt.bar(route_ids, trip_freqs)
    plt.title("Top 10 Routes by Route Frequency")
    plt.xlabel("Route ID")
    plt.ylabel("Route Frequency")    

    results_dict = dict(results)
    trips_results_dict = dict(trips_results)

    avg_results = []
    for key in results_dict:
        avg_results.append((key, round(results_dict[key]/trips_results_dict[key], 2)))
    sorted_avg_results = sorted(avg_results, key=itemgetter(1), reverse = True)

    route_ids = []
    avg_stops = []
    print("Top 10 Busiest Routes (by stop update average):")
    for row in sorted_avg_results[0:10]:
        route_ids.append(row[0])
        avg_stops.append(row[1])
        print(f"Route ID: {row[0]}\t has {row[1]}\t stop updates, on average.")

    plt.figure(4)
    plt.bar(route_ids, avg_stops)
    plt.title("Top 10 Busiest Routes (by stop update average)")
    plt.xlabel("Route ID")
    plt.ylabel("Average Stop Updates")
    
        

    con.close()

def cancel_trends(span):
    con = sqlite3.connect("shuttle.db")
    cur = con.cursor()

    query = """
        SELECT
            route_id,
            COUNT(CASE WHEN schedule_relationship = 'CANCELED' THEN 1 END) AS canceled_trips,
            COUNT(*) AS total_trips,
            COUNT(CASE WHEN schedule_relationship = 'CANCELED' AND feed_timestamp = :earliest THEN 1 END) AS canceled_earlier_trips,
            COUNT(CASE WHEN feed_timestamp = :earliest THEN 1 END) AS total_earlier_trips,
            ROUND(SUM(CASE WHEN schedule_relationship = 'CANCELED' AND feed_timestamp = :earliest THEN 1.0 ELSE 0.0 END) / SUM(CASE WHEN feed_timestamp = :earliest THEN 1.0 ELSE 0.0 END), 2) AS early_cancel_rate,
            COUNT(CASE WHEN schedule_relationship = 'CANCELED' AND feed_timestamp = :latest THEN 1 END) AS canceled_later_trips,
            COUNT(CASE WHEN feed_timestamp = :latest THEN 1 END) AS total_later_trips,
            ROUND(SUM(CASE WHEN schedule_relationship = 'CANCELED' AND feed_timestamp = :latest THEN 1.0 ELSE 0.0 END) / SUM(CASE WHEN feed_timestamp = :latest THEN 1.0 ELSE 0.0 END), 2) AS late_cancel_rate,
            ROUND(SUM(CASE WHEN schedule_relationship = 'CANCELED' AND feed_timestamp = :latest THEN 1.0 ELSE 0.0 END) / SUM(CASE WHEN feed_timestamp = :latest THEN 1.0 ELSE 0.0 END) - SUM(CASE WHEN schedule_relationship = 'CANCELED' AND feed_timestamp = :earliest THEN 1.0 ELSE 0.0 END) / SUM(CASE WHEN feed_timestamp = :earliest THEN 1.0 ELSE 0.0 END), 2) AS change_in_rate
        FROM trips
        GROUP BY route_id
        HAVING change_in_rate IS NOT NULL
        ORDER BY change_in_rate DESC;
    """
    params = {
        "earliest": span[0],
        "latest": span[1]
    }

    cur.execute(query, params)
    results = cur.fetchall()

    x_date = ["June 23, 2026", "June 30, 2026"]
    plt.figure(5)
    print("Largest Increases in Cancelation Rate from 6/23/26 to 6/30/26:")

    for row in results[0:5]:
        y_cancel_rate = [row[5], row[8]]
        plt.plot(x_date, y_cancel_rate, label=row[0])
        print(f"Route ID: {row[0]}\twith a change of {row[9]}\t(from {row[5]}\tto {row[8]})")
    plt.title("Top 10 Largest Increases in Cancelation Rate from 6/23/26 to 6/30/26")
    plt.xlabel("Route ID")
    plt.ylabel("Cancelation Rate")
    plt.legend()

    plt.figure(6)
    print("Largest Decreases in Cancelation Rate from 6/23/26 to 6/30/26:")
    for row in results[-1:-6:-1]:
        y_cancel_rate = [row[5], row[8]]
        plt.plot(x_date, y_cancel_rate, label=row[0])
        print(f"Route ID: {row[0]}\twith a change of {row[9]}\t(from {row[5]}\tto {row[8]})")
    plt.title("Top 10 Largest Decreases in Cancelation Rate from 6/23/26 to 6/30/26")
    plt.xlabel("Route ID")
    plt.ylabel("Cancelation Rate")
    plt.legend()

def stop_trends(span):
    con = sqlite3.connect("shuttle.db")
    cur = con.cursor()

    query = """
        SELECT
            trips.route_id,
            COUNT(CASE WHEN fd_timestamp = :earliest THEN 1 END) AS early_stops,
            COUNT(CASE WHEN fd_timestamp = :latest THEN 1 END) AS late_stops,
            SUM(CASE WHEN fd_timestamp = :latest THEN 1 END) - SUM(CASE WHEN fd_timestamp = :earliest THEN 1 END) AS change_in_stops,
            COUNT(*) AS total_stops
        FROM stops
        JOIN trips
            ON stops.t_id = trips.trip_id
                AND stops.st_date = trips.start_date
                AND stops.fd_timestamp = trips.feed_timestamp
        GROUP BY trips.route_id
        ORDER BY change_in_stops DESC;
    """

    params = {
        "earliest": span[0],
        "latest": span[1]
    }

    cur.execute(query, params)
    results = cur.fetchall()

    x_date = ["June 23, 2026", "June 30, 2026"]
    plt.figure(7)
    print("Largest Increases in Stop Updates from 6/23/26 to 6/30/26:")
    for row in results[0:5]:
        y_stop_updates = [0, row[2] - row[1]]
        plt.plot(x_date, y_stop_updates, label=row[0])
        print(f"Route ID: {row[0]}\twith a change of {row[3]}\t(from {row[1]}\tto {row[2]})")
    plt.title("Top 10 Largest Increases in Stop Updates from 6/23/26 to 6/30/26")
    plt.xlabel("Route ID")
    plt.ylabel("Change in Stop Updates")
    plt.legend()

    plt.figure(8)
    print("Largest Decreases in Stop Updates from 6/23/26 to 6/30/26:")
    for row in results[-1:-6:-1]:
        y_stop_updates = [0, row[2]-row[1]]
        plt.plot(x_date, y_stop_updates, label=row[0])
        print(f"Route ID: {row[0]}\twith a change of {row[3]}\t(from {row[1]}\tto {row[2]})")
    plt.title("Top 10 Largest Decreases in Stop Updates from 6/23/26 to 6/30/26")
    plt.xlabel("Route ID")
    plt.ylabel("Change in Stop Updates")
    plt.legend()
    

def find_timestamps():
    con = sqlite3.connect("shuttle.db")
    cur = con.cursor()

    query = """
        SELECT DISTINCT feed_timestamp FROM trips ORDER BY feed_timestamp
    """

    cur.execute(query)
    results = cur.fetchall()

    timestamps = [row[0] for row in results]

    return (timestamps[0], timestamps[-1])
    
if __name__ == "__main__":
    print("TOTAL STATS:")
    cancellation_rate()
    most_stop_updates()
    print("Historical Trends")
    timespan = find_timestamps()
    cancel_trends(timespan)
    stop_trends(timespan)
    plt.show()
    