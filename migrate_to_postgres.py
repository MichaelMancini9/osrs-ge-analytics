import sqlite3
import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

def get_sqlite_connection():
    return sqlite3.connect("osrs_data.db")

def get_postgres_connection():
    return psycopg2.connect(
        host="localhost",
        port=5432,
        dbname="osrs_data",
        user="osrs_user",
        password=os.getenv("POSTGRES_PASSWORD")
    )

def migrate_items(sqlite_conn, pg_conn):
    sqlite_cur = sqlite_conn.cursor()
    sqlite_cur.execute("SELECT item_id, name, members, lowalch, ge_limit, value, highalch, examine, icon FROM items")
    rows = sqlite_cur.fetchall()

    pg_cur = pg_conn.cursor()
    pg_cur.executemany("""
        INSERT INTO items (item_id, name, members, lowalch, ge_limit, value, highalch, examine, icon)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (item_id) DO NOTHING
    """, rows)
    pg_conn.commit()
    print(f"Migrated {len(rows)} rows into items")

def migrate_price_snapshots(sqlite_conn, pg_conn):
    sqlite_cur = sqlite_conn.cursor()
    sqlite_cur.execute("SELECT item_id, high_price, high_time, low_price, low_time, collected_at FROM price_snapshots")
    rows = sqlite_cur.fetchall()

    pg_cur = pg_conn.cursor()
    pg_cur.executemany("""
        INSERT INTO price_snapshots (item_id, high_price, high_time, low_price, low_time, collected_at)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, rows)
    pg_conn.commit()
    print(f"Migrated {len(rows)} rows into price_snapshots")

def migrate_price_changes(sqlite_conn, pg_conn):
    sqlite_cur = sqlite_conn.cursor()
    sqlite_cur.execute("SELECT item_id, current_price, price_24h_ago, percent_change, calculated_at FROM price_changes")
    rows = sqlite_cur.fetchall()

    pg_cur = pg_conn.cursor()
    pg_cur.executemany("""
        INSERT INTO price_changes (item_id, current_price, price_24h_ago, percent_change, calculated_at)
        VALUES (%s, %s, %s, %s, %s)
        ON CONFLICT (item_id) DO NOTHING
    """, rows)
    pg_conn.commit()
    print(f"Migrated {len(rows)} rows into price_changes")

def migrate_volatility(sqlite_conn, pg_conn):
    sqlite_cur = sqlite_conn.cursor()
    sqlite_cur.execute("SELECT item_id, mean_price, std_dev, relative_volatility, calculated_at FROM volatility")
    rows = sqlite_cur.fetchall()

    pg_cur = pg_conn.cursor()
    pg_cur.executemany("""
        INSERT INTO volatility (item_id, mean_price, std_dev, relative_volatility, calculated_at)
        VALUES (%s, %s, %s, %s, %s)
        ON CONFLICT (item_id) DO NOTHING
    """, rows)
    pg_conn.commit()
    print(f"Migrated {len(rows)} rows into volatility")

def migrate_moving_averages(sqlite_conn, pg_conn):
    sqlite_cur = sqlite_conn.cursor()
    sqlite_cur.execute("SELECT item_id, window_size, moving_avg, calculated_at FROM moving_averages")
    rows = sqlite_cur.fetchall()

    pg_cur = pg_conn.cursor()
    pg_cur.executemany("""
        INSERT INTO moving_averages (item_id, window_size, moving_avg, calculated_at)
        VALUES (%s, %s, %s, %s)
        ON CONFLICT (item_id, window_size) DO NOTHING
    """, rows)
    pg_conn.commit()
    print(f"Migrated {len(rows)} rows into moving_averages")

def migrate_momentum(sqlite_conn, pg_conn):
    sqlite_cur = sqlite_conn.cursor()
    sqlite_cur.execute("SELECT item_id, short_window, long_window, momentum_pct, calculated_at FROM momentum")
    rows = sqlite_cur.fetchall()

    pg_cur = pg_conn.cursor()
    pg_cur.executemany("""
        INSERT INTO momentum (item_id, short_window, long_window, momentum_pct, calculated_at)
        VALUES (%s, %s, %s, %s, %s)
        ON CONFLICT (item_id, short_window, long_window) DO NOTHING
    """, rows)
    pg_conn.commit()
    print(f"Migrated {len(rows)} rows into momentum")

def migrate_z_scores(sqlite_conn, pg_conn):
    sqlite_cur = sqlite_conn.cursor()
    sqlite_cur.execute("SELECT item_id, z_score, calculated_at FROM z_scores")
    rows = sqlite_cur.fetchall()

    pg_cur = pg_conn.cursor()
    pg_cur.executemany("""
        INSERT INTO z_scores (item_id, z_score, calculated_at)
        VALUES (%s, %s, %s)
        ON CONFLICT (item_id) DO NOTHING
    """, rows)
    pg_conn.commit()
    print(f"Migrated {len(rows)} rows into z_scores")

if __name__ == "__main__":
    sqlite_conn = get_sqlite_connection()
    pg_conn = get_postgres_connection()

    migrate_items(sqlite_conn, pg_conn)
    migrate_price_snapshots(sqlite_conn, pg_conn)
    migrate_price_changes(sqlite_conn, pg_conn)
    migrate_volatility(sqlite_conn, pg_conn)
    migrate_moving_averages(sqlite_conn, pg_conn)
    migrate_momentum(sqlite_conn, pg_conn)
    migrate_z_scores(sqlite_conn, pg_conn)

    sqlite_conn.close()
    pg_conn.close()
    print("Done")