from db import get_connection
import time

query = """
WITH window_prices AS (
    SELECT item_id, high_price
    FROM price_snapshots
    WHERE collected_at >= (SELECT MAX(collected_at) FROM price_snapshots) - 1800
      AND high_price IS NOT NULL
),
stats AS (
    SELECT item_id, AVG(high_price) AS mean_price, COUNT(*) AS n
    FROM window_prices
    GROUP BY item_id
    HAVING COUNT(*) >= 3
),
squared_diffs AS (
    SELECT 
        w.item_id,
        (w.high_price - s.mean_price) * (w.high_price - s.mean_price) AS sq_diff
    FROM window_prices w
    JOIN stats s ON w.item_id = s.item_id
)
SELECT 
    s.item_id,
    s.mean_price,
    SQRT(AVG(sd.sq_diff)) AS std_dev,
    SQRT(AVG(sd.sq_diff)) / s.mean_price AS relative_volatility
FROM stats s
JOIN squared_diffs sd ON s.item_id = sd.item_id
GROUP BY s.item_id, s.mean_price;
"""

def calculate_volatility(conn):
    cur = conn.cursor()
    cur.execute(query)
    return cur.fetchall()

def store_volatility(conn, rows, calculated_at):
    data = [(item_id, mean_price, std_dev, relative_volatility, calculated_at) for item_id, mean_price, std_dev, relative_volatility in rows]
    cur = conn.cursor()
    cur.executemany("""
        INSERT INTO volatility (item_id, mean_price, std_dev, relative_volatility, calculated_at)
        VALUES (%s, %s, %s, %s, %s)
        ON CONFLICT(item_id) DO UPDATE SET
            mean_price = excluded.mean_price,
            std_dev = excluded.std_dev,
            relative_volatility = excluded.relative_volatility,
            calculated_at = excluded.calculated_at
    """, data)
    conn.commit()

if __name__ == "__main__":
    conn = get_connection()
    
    rows = calculate_volatility(conn)
    print(f"Calculated volatility for {len(rows)} items")
    
    calculated_at = int(time.time())
    store_volatility(conn, rows, calculated_at)
    
    conn.close()
    print("Done")   