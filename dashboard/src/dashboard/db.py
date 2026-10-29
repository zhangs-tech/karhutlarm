import sqlite3
import threading
import time
from pathlib import Path

SCHEMA = """
CREATE TABLE IF NOT EXISTS readings (
    id       INTEGER PRIMARY KEY AUTOINCREMENT,
    ts       REAL NOT NULL,  -- unix epoch seconds, set when the message arrives
    gas      REAL NOT NULL,
    temp     REAL NOT NULL,
    humidity REAL NOT NULL,
    status   TEXT NOT NULL
)
"""


class ReadingStore:
    """Shared by the MQTT thread (writes) and API handlers (reads)."""

    def __init__(self, path: Path):
        self._conn = sqlite3.connect(path, check_same_thread=False)
        self._conn.row_factory = sqlite3.Row
        self._lock = threading.Lock()
        with self._lock:
            self._conn.execute("PRAGMA journal_mode=WAL")
            self._conn.execute(SCHEMA)
            self._conn.commit()

    def add(self, gas: float, temp: float, humidity: float, status: str) -> int:
        with self._lock:
            cur = self._conn.execute(
                "INSERT INTO readings (ts, gas, temp, humidity, status)"
                " VALUES (?, ?, ?, ?, ?)",
                (time.time(), gas, temp, humidity, status),
            )
            self._conn.commit()
            return cur.lastrowid

    def after(self, after_id: int, limit: int) -> list[dict]:
        with self._lock:
            rows = self._conn.execute(
                "SELECT * FROM readings WHERE id > ? ORDER BY id LIMIT ?",
                (after_id, limit),
            ).fetchall()
        return [dict(r) for r in rows]

    def latest(self, limit: int) -> list[dict]:
        with self._lock:
            rows = self._conn.execute(
                "SELECT * FROM readings ORDER BY id DESC LIMIT ?", (limit,)
            ).fetchall()
        return [dict(r) for r in reversed(rows)]

    def close(self) -> None:
        with self._lock:
            self._conn.close()
