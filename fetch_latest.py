import requests
import time
from db import get_connection, BASE_URL, HEADERS


def fetch_latest_prices():
    url = f"{BASE_URL}/latest"
    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()
    return response.json()


def build_rows(items, collected_at):
    rows = []
    for item_id_str, price_data in items.items():
        row = (
            int(item_id_str),
            price_data.get("high"),
            price_data.get("highTime"),
            price_data.get("low"),
            price_data.get("lowTime"),
            collected_at
        )
        rows.append(row)
    return rows


def insert_snapshot(conn, rows):
    cur = conn.cursor()
    cur.executemany("""
        INSERT INTO price_snapshots (item_id, high_price, high_time, low_price, low_time, collected_at)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, rows)
    conn.commit()


if __name__ == "__main__":
    data = fetch_latest_prices()
    items = data["data"]
    print(f"Fetched prices for {len(items)} items")

    collected_at = int(time.time())
    rows = build_rows(items, collected_at)

    conn = get_connection()
    insert_snapshot(conn, rows)
    conn.close()

    print(f"Inserted {len(rows)} rows into Postgres")
