from db import get_connection
import time

query = """
WITH ranked AS (
    SELECT
        item_id,
        high_price,
        collected_at,
        ROW_NUMBER() OVER (
            PARTITION BY item_id
            ORDER BY collected_at DESC
        ) AS rn
    FROM price_snapshots
    WHERE high_price IS NOT NULL
)
SELECT 
    item_id,
    AVG(high_price) AS moving_avg
FROM ranked
WHERE rn <= %s
GROUP BY item_id
"""

def calculate_moving_averages(conn, window_size):
    cur = conn.cursor()
    cur.execute(query, (window_size,))
    return cur.fetchall()

def store_moving_averages(conn, rows, window_size, calculated_at):
    data = [(item_id, window_size, avg, calculated_at) for item_id, avg in rows]
    cur = conn.cursor()
    cur.executemany("""
        INSERT INTO moving_averages (item_id, window_size, moving_avg, calculated_at)
        VALUES (%s, %s, %s, %s)
        ON CONFLICT(item_id, window_size) DO UPDATE SET
            moving_avg = excluded.moving_avg,
            calculated_at = excluded.calculated_at
    """, data)
    conn.commit()

WINDOW_PRESETS = [36, 288, 2016]

if __name__ == "__main__":
    conn = get_connection()
    calculated_at = int(time.time())

    for window in WINDOW_PRESETS:
         rows = calculate_moving_averages(conn, window)
         print(f"Window {window}: calculated averages for {len(rows)} items")
         store_moving_averages(conn, rows, window, calculated_at)

    conn.close()
    print("Done")