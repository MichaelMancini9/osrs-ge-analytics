from db import get_connection
import time

query  = """
SELECT 
    latest.item_id,
    ROUND (((latest.high_price - ma.moving_avg) / vol.std_dev)::NUMERIC, 2) AS z_score
FROM (
    SELECT item_id, high_price
    FROM price_snapshots
    WHERE collected_at = (SELECT MAX(collected_at) FROM price_snapshots)
        AND high_price IS NOT NULL
) latest
JOIN moving_averages ma
    ON latest.item_id = ma.item_id
    AND ma.window_size = %s
JOIN volatility vol
    ON latest.item_id = vol.item_id
    AND  vol.std_dev != 0
"""

def calculate_z_scores(conn, window_size):
    cur = conn.cursor()
    cur.execute(query, (window_size,))
    return cur.fetchall()

def store_z_scores(conn, rows, calculated_at):
    data = [(item_id, z, calculated_at) for item_id, z in rows]
    cur = conn.cursor()
    cur.executemany("""
            INSERT INTO z_scores (item_id, z_score, calculated_at)
            VALUES (%s, %s, %s)
            ON CONFLICT(item_id) DO UPDATE SET
                     z_score = excluded.z_score,
                     calculated_at = excluded.calculated_at
    """, data)
    conn.commit()
    
if __name__ == "__main__":
    conn = get_connection()
    calculated_at = int(time.time())

    rows = calculate_z_scores(conn, window_size=36)
    print(f"Calculated z-scores for {len(rows)} items")
    store_z_scores(conn, rows, calculated_at)

    conn.close()
    print("Done")