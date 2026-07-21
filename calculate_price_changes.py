from db import get_connection
import time

query = """
WITH latest AS(
    SELECT item_id, high_price, collected_at
    FROM price_snapshots
    WHERE collected_at = (SELECT MAX(collected_at) FROM price_snapshots)
    ),
     past AS (
        SELECT ps.item_id, ps.high_price
        FROM price_snapshots ps
        JOIN (
            SELECT item_id, MAX(collected_at) AS max_collected_at
            FROM price_snapshots
            WHERE collected_at <= (SELECT MAX(collected_at) FROM price_snapshots) - 86400
            GROUP BY item_id
        ) latest_past     
        ON ps.item_id = latest_past.item_id
        AND ps.collected_at = latest_past.max_collected_at
    )
    SELECT 
        latest.item_id,
        latest.high_price AS current_price,
        past.high_price AS price_24h_ago,
        ROUND(
            (CAST(latest.high_price AS REAL) - past.high_price) / past.high_price * 100, 2)
            AS percent_change
    FROM latest
    JOIN past ON latest.item_id = past.item_id
"""

def calculate_24h_changes(conn):
    return conn.execute(query).fetchall()

def store_price_changes(conn, rows, calculated_at):
    data = [(item_id, current, past, pct, calculated_at) for item_id, current, past, pct in rows]
    conn.executemany("""
        INSERT INTO price_changes (item_id, current_price, price_24h_ago, percent_change, calculated_at)
        VALUES (?, ?, ?, ?, ?)
        ON CONFLICT(item_id) DO UPDATE SET
            current_price = excluded.current_price,
            price_24h_ago = excluded.price_24h_ago,
            percent_change = excluded.percent_change,
            calculated_at = excluded.calculated_at
    """, data)
    conn.commit()

if __name__ == "__main__":
    conn = get_connection()
    
    rows = calculate_24h_changes(conn)
    print(f"Calculated changes for {len(rows)} items")
    
    calculated_at = int(time.time())
    store_price_changes(conn, rows, calculated_at)
    
    conn.close()
    print("Done")