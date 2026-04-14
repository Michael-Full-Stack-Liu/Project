import sqlite3
import requests
from datetime import datetime
import os
import json

DB_PATH = "app_database.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    # Create table for METAR observations
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS metar_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            station_id TEXT,
            observed_at TEXT UNIQUE,
            temp_c REAL,
            dew_point_c REAL,
            wind_speed_kt REAL,
            wind_dir INTEGER,
            pressure_hpa REAL,
            raw_text TEXT,
            fetched_at TEXT
        )
    ''')
    
    # Create table for predictions
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS predictions (
            target_date TEXT PRIMARY KEY,
            predicted_max_temp REAL,
            created_at TEXT
        )
    ''')
    conn.commit()
    conn.close()

def fetch_metar_ksea():
    url = "https://api.weather.gov/stations/KSEA/observations/latest"
    headers = {"User-Agent": "SeattlePolymarketDashboard/1.0 (contact@example.com)"}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()
        props = data.get("properties", {})
        
        station_id = "KSEA"
        observed_at = props.get("timestamp")
        temp_c = props.get("temperature", {}).get("value")
        dew_point_c = props.get("dewpoint", {}).get("value")
        # Wind speed in m/s from API, convert to knots or keep as m/s. API gives km/h or m/s.
        wind_speed_val = props.get("windSpeed", {}).get("value") 
        wind_dir = props.get("windDirection", {}).get("value")
        pressure_pa = props.get("barometricPressure", {}).get("value")
        pressure_hpa = pressure_pa / 100.0 if pressure_pa else None
        raw_text = props.get("rawMessage", "")
        
        return {
            "station_id": station_id,
            "observed_at": observed_at,
            "temp_c": temp_c,
            "dew_point_c": dew_point_c,
            "wind_speed_kt": wind_speed_val,
            "wind_dir": wind_dir,
            "pressure_hpa": pressure_hpa,
            "raw_text": raw_text,
            "fetched_at": datetime.utcnow().isoformat()
        }
    except Exception as e:
        print(f"Error fetching METAR: {e}")
        return None

def save_metar(record):
    if not record or not record.get("observed_at"):
        return
        
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO metar_data (
                station_id, observed_at, temp_c, dew_point_c, 
                wind_speed_kt, wind_dir, pressure_hpa, raw_text, fetched_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            record["station_id"], record["observed_at"], record["temp_c"],
            record["dew_point_c"], record["wind_speed_kt"], record["wind_dir"],
            record["pressure_hpa"], record["raw_text"], record["fetched_at"]
        ))
        conn.commit()
        print(f"Saved METAR observation for {record['observed_at']} with Temp: {record['temp_c']}C")
    except sqlite3.IntegrityError:
        print(f"Observation for {record['observed_at']} already exists.")
    finally:
        conn.close()

if __name__ == "__main__":
    init_db()
    data = fetch_metar_ksea()
    save_metar(data)
