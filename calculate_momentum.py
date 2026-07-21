from db import get_connection
import time

query = """
SELECT
    s.item_id,
    ROUND(((s.moving_avg - l.moving_avg) / l.moving_avg * 100)::NUMERIC, 2) AS momentum_pct
FROM moving_averages s
JOIN moving_averages l
    ON s.item_id = l.item_id
WHERE s.window_size = %s
    AND l.window_size = %s
"""

def calculate_momentum(conn, short_window, long_window):
    cur = conn.cursor()
    cur.execute(query, (short_window,long_window))
    return cur.fetchall()

def store_momentum(conn, rows, short_window, long_window, calculated_at):
    data = [(item_id, short_window, long_window, momentum_pct, calculated_at) for item_id, momentum_pct in rows]
    cur = conn.cursor()
    cur.executemany("""
        INSERT INTO momentum (item_id, short_window, long_window, momentum_pct, calculated_at)
        VALUES (%s, %s, %s, %s, %s)
        ON CONFLICT(item_id, short_window, long_window) DO UPDATE SET
            momentum_pct = excluded.momentum_pct,
            calculated_at = excluded.calculated_at                 
    """, data)
    conn.commit()

MOMENTUM_PAIRS = [(36,288), (288, 2016)]

if __name__ == "__main__":
    conn = get_connection()
    calculated_at = int(time.time())

    for short_window, long_window in MOMENTUM_PAIRS:
        rows = calculate_momentum(conn, short_window, long_window)
        print(f"Pair {short_window} vs {long_window}: calculated momentum for {len(rows)} items")
        store_momentum(conn, rows, short_window, long_window, calculated_at)

    conn.close()
    print("Done")