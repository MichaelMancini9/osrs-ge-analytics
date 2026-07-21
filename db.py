import sqlite3
import os
from dotenv import load_dotenv


BASE_URL = "https://prices.runescape.wiki/api/v1/osrs"
HEADERS = {"User-Agent": "osrs-ge-analytics learning project - {os.environ.get('PRIVATE_EMAIL')}"}

def get_connection():
    conn = sqlite3.connect("osrs_data.db")
    conn.execute("""
                 CREATE TABLE IF NOT EXISTS price_snapshots(
                     id INTEGER PRIMARY KEY AUTOINCREMENT,
                     item_id INTEGER NOT NULL,
                     high_price INTEGER,
                     high_time INTEGER,
                     low_price INTEGER,
                     low_time INTEGER,
                     collected_at INTEGER NOT NULL
                 )
                 """)
    conn.execute("""
                 CREATE TABLE IF NOT EXISTS items(
                    item_id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL,
                    members INTEGER NOT NULL,
                    lowalch INTEGER,
                    ge_limit INTEGER,
                    value INTEGER,
                    highalch INTEGER,
                    examine TEXT,
                    icon TEXT
                 )
                """)
    
    conn.execute("""
                 CREATE TABLE IF NOT EXISTS price_changes (
                    item_id INTEGER PRIMARY KEY,
                 current_price INTEGER,
                 price_24h_ago INTEGER,
                 percent_change REAL,
                 calculated_at INTEGER NOT NULL
                 )
                """)
    
    conn.execute("""
                 CREATE TABLE IF NOT EXISTS volatility(
                 item_id INTEGER PRIMARY KEY,
                 mean_price REAL,
                 std_dev REAL,
                 relative_volatility REAL,
                 calculated_at INTEGER NOT NULL
                 )
                """)
    conn.execute("""
                 CREATE TABLE IF NOT EXISTS moving_averages (
                 item_id INTEGER NOT NULL,
                 window_size INTEGER NOT NULL,
                 moving_avg REAL NOT NULL,
                 calculated_at INTEGER NOT NULL,
                 PRIMARY KEY (item_id, window_size))
                 """)
    
    conn.execute("""
                  CREATE TABLE IF NOT EXISTS momentum (
                 item_id INTEGER NOT NULL,
                 short_window INTEGER NOT NULL,
                 long_window INTEGER NOT NULL,
                 momentum_pct REAL NOT NULL,
                 calculated_at INTEGER NOT NULL,
                 PRIMARY KEY (item_id, short_window, long_window))
                 """)
    
    conn.execute("""
                  CREATE TABLE IF NOT EXISTS z_scores (
                 item_id INTEGER NOT NULL,
                 z_score REAL NOT NULL,
                 calculated_at INTEGER NOT NULL,
                 PRIMARY KEY (item_id))
                 """)

    return conn