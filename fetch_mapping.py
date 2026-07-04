from db import get_connection, BASE_URL, HEADERS
import requests
import json
import sqlite3
import time

def fetch_mapping():
    url = f"{BASE_URL}/mapping"
    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()
    return response.json()


def build_item_rows(mapping):
    rows = []
    for item in mapping:
        row = (
            item["id"],
            item["name"],
            int(item["members"]),
            item.get("lowalch"),
            item.get("limit"),
            item.get("value"),
            item.get("highalch"),
            item.get("examine"),
            item.get("icon")
        )
        rows.append(row)
    return rows

def upsert_items(conn,rows):
    conn.executemany("""
        INSERT INTO items (item_id,  name, members, lowalch, ge_limit, value, highalch, examine, icon)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(item_id) DO UPDATE SET
            name = excluded.name,
            members = excluded.members,
            lowalch = excluded.lowalch,
            ge_limit = excluded.ge_limit,
            value = excluded.value,
            highalch = excluded.highalch,
            examine = excluded.examine,
            icon = excluded.icon
        """, rows)
    conn.commit()

if __name__ == "__main__":
    mapping = fetch_mapping()
    print(f"Fetched {len(mapping)} items definitions")
    
    rows = build_item_rows(mapping)

    conn = get_connection()
    upsert_items(conn, rows)
    conn.close()

    print(f"Upserted {len(rows)} rows into items table")