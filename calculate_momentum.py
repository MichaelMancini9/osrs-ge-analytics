from db import get_connection
import time

query = """
SELECT
    s.item_id,
    ROUND((s.moving_avg - l.moving_avg) / l.moving_avg * 100, 2) AS momentum_pct
FROM moving_averages s
JOIN moving_averages l
    ON s.item_id = l.item_id
WHERE s.window_size = ?
    AND l.window_size = ?
"""

def calculate_momentum(conn, short_window, long_window):
    return conn.execute(query, (short_window,long_window)).fetchall()

def store_momentum(conn, rows, short_window, long_window, calculated_at):
    data = [(item_id, short_window, long_window, momentum_pct, calculated_at) for item_id, momentum_pct in rows]
    conn.executemany("""
        INSERT INTO momentum (item_id, short_window, long_window, momentum_pct, calculated_at)
        VALUES (?, ?, ?, ?, ?)
        ON CONFLICT(item_id, short_window, long_window) DO UPDATE SET
            momentum_pct = excluded.momentum_pct,
            calculated_at = excluded.calculated_at                 
    """, data)
    conn.commit()

MOMENTUM_PAIRS = [(6, 48), (48, 336)]

if __name__ == "__main__":
    conn = get_connection()
    calculated_at = int(time.time())

    for short_window, long_window in MOMENTUM_PAIRS:
        rows = calculate_momentum(conn, short_window, long_window)
        print(f"Pair {short_window} vs {long_window}: calculated momentum for {len(rows)} items")
        store_momentum(conn, rows, short_window, long_window, calculated_at)

    conn.close()
    print("Done")