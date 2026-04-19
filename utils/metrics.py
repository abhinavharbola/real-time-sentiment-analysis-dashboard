# Calculates key performance indicators (KPIs)
# aggregates sentiment metrics across multiple temporal windows using direct database queries

import sqlite3
import pandas as pd
from datetime import datetime, timedelta

DB_PATH = "sentiment.db"

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def fetch_temporal_data(hours: int = 1) -> pd.DataFrame:
    # CHANGED: Use utcnow() to match SQLite's default CURRENT_TIMESTAMP
    time_threshold = datetime.utcnow() - timedelta(hours=hours)
    conn = get_db_connection()
    query = f"SELECT * FROM analytics WHERE timestamp >= '{time_threshold.strftime('%Y-%m-%d %H:%M:%S')}'"
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

def calculate_kpis(df: pd.DataFrame) -> dict:
    if df.empty:
        return {
            "total_records": 0, "positive_pct": 0.0, "negative_pct": 0.0,
            "avg_latency_ms": 0.0, "avg_confidence": 0.0, "throughput_per_min": 0.0
        }
    
    total = len(df)
    pos_count = len(df[df['sentiment'] == 'POSITIVE'])
    
    time_span_minutes = (pd.to_datetime(df['timestamp'].max()) - pd.to_datetime(df['timestamp'].min())).total_seconds() / 60
    throughput = total / time_span_minutes if time_span_minutes > 0 else total

    return {
        "total_records": total,
        "positive_pct": round((pos_count / total) * 100, 1),
        "negative_pct": round(((total - pos_count) / total) * 100, 1),
        "avg_latency_ms": round(df['latency_ms'].mean(), 2),
        "avg_confidence": round(df['confidence'].mean(), 3),
        "throughput_per_min": round(throughput, 1)
    }