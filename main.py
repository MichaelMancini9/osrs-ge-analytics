from fastapi import FastAPI
from db import get_connection
from datetime import datetime, timezone

app = FastAPI()

@app.get("/items/{item_id}")
def get_item(item_id: int):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT
            i.item_id,
            i.name,
            pc.current_price,
            pc.percent_change,
            v.std_dev,
            v.relative_volatility,
            z.z_score
        FROM items i
        LEFT JOIN price_changes pc ON i.item_id = pc.item_id
        LEFT JOIN volatility v ON i.item_id = v.item_id
        LEFT JOIN z_scores z ON i.item_id = z.item_id
        WHERE i.item_id = %s
    """, (item_id,))

    row = cur.fetchone()
    conn.close()

    if row is None:
        return {"error": "Item not found"}

    return {
        "item_id": row[0],
        "name": row[1],
        "current_price": row[2],
        "percent_change_24h": row[3],
        "std_dev": row[4],
        "relative_volatility": row[5],
        "z_score": row[6]
    }


PERIOD_CONFIG = {
    "1d": {"seconds": 86400, "bucket": 300},      # 5 min 
    "1w": {"seconds": 604800, "bucket": 1800},     # 30 min
    "2w": {"seconds": 1209600, "bucket": 3600},    # 1 hour
    "1m": {"seconds": 2592000, "bucket": 14400},   # 4 hours
}

@app.get("/items/{item_id}/history")
def get_item_history(item_id: int, period: str = "1d"):
    config = PERIOD_CONFIG.get(period, PERIOD_CONFIG["1d"])
    seconds = config["seconds"]
    bucket = config["bucket"]

    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT
            (p.collected_at / %s) * %s AS bucket_time,
            AVG(p.high_price) AS price,
            i.name,
            i.icon
        FROM price_snapshots p
        JOIN items i
        ON i.item_id = p.item_id
        WHERE p.item_id = %s
          AND p.collected_at >= EXTRACT(EPOCH FROM NOW()) - %s
          AND p.high_price IS NOT NULL
        GROUP BY bucket_time, i.name, i.icon
        ORDER BY bucket_time ASC
    """, (bucket, bucket, item_id, seconds))
    rows = cur.fetchall()
    conn.close()

    name = rows[0][2]
    icon = rows[0][3]
    icon_fixed = icon.replace(" ", "_")

    return {
        "icon" : icon_fixed,
        "name" : name,
        "item_id": item_id,
        "period": period,
        "data_points": [
            {
                "timestamp": datetime.fromtimestamp(row[0], tz=timezone.utc).isoformat().replace("+00:00", "Z"),
                "price": round(float(row[1]), 2)
            }
            for row in rows
        ]
    }