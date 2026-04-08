import sqlite3
import json
import os
import threading

class OfflineQueue:
    """Thread-safe local SQLite queue buffer for offline resilience."""
    def __init__(self, db_path="offline_queue.db"):
        self.db_path = db_path
        self.lock = threading.Lock()
        self._init_db()

    def _init_db(self):
        with self.lock:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS pending_logs (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        payload TEXT NOT NULL
                    )
                """)

    def push(self, payload):
        with self.lock:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("INSERT INTO pending_logs (payload) VALUES (?)", (json.dumps(payload),))

    def get_pending(self):
        with self.lock:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("SELECT id, payload FROM pending_logs ORDER BY id ASC")
                return cursor.fetchall()

    def remove(self, log_id):
        with self.lock:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("DELETE FROM pending_logs WHERE id = ?", (log_id,))
