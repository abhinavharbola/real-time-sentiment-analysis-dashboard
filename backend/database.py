# Handles asynchronous SQLite database initialization,
# high-throughput batch insertions, and metric aggregations for the real-time sentiment dashboard

import aiosqlite
import logging
from datetime import datetime
from typing import List, Dict

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DB_PATH = "sentiment.db"

async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute('''
            CREATE TABLE IF NOT EXISTS analytics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                text TEXT,
                sentiment TEXT,
                confidence REAL,
                latency_ms REAL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        await db.commit()
    logger.info("Database initialized successfully.")

async def insert_batch_predictions(records: List[Dict]):
    query = """
        INSERT INTO analytics (text, sentiment, confidence, latency_ms)
        VALUES (:text, :sentiment, :confidence, :latency_ms)
    """
    try:
        async with aiosqlite.connect(DB_PATH) as db:
            await db.executemany(query, records)
            await db.commit()
    except Exception as e:
        logger.error(f"Database insertion failed: {e}")
        raise

async def fetch_metrics() -> Dict:
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT COUNT(*) FROM analytics") as cursor:
            total_requests = await cursor.fetchone()
        
        async with db.execute("SELECT AVG(latency_ms) FROM analytics") as cursor:
            avg_latency = await cursor.fetchone()

    return {
        "total_processed": total_requests[0] if total_requests else 0,
        "average_latency_ms": round(avg_latency[0], 2) if avg_latency[0] else 0.0
    }