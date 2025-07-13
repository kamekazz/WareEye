import sqlite3
import time
from typing import Dict, List

DB_PATH = "scans.db"
_last_scanned_at = 0


def init_db() -> None:
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        """CREATE TABLE IF NOT EXISTS scans (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            code TEXT NOT NULL,
            timestamp INTEGER
        )"""
    )
    conn.commit()
    conn.close()


def save_scan(code: str, cooldown: int = 5) -> None:
    now = int(time.time())
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        "SELECT timestamp FROM scans WHERE code=? ORDER BY timestamp DESC LIMIT 1",
        (code,),
    )
    row = c.fetchone()
    if row is None or now - row[0] > cooldown:
        c.execute("INSERT INTO scans (code, timestamp) VALUES (?, ?)", (code, now))
        conn.commit()
        global _last_scanned_at
        _last_scanned_at = now
    conn.close()


def get_all() -> List[Dict]:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM scans ORDER BY timestamp DESC")
    rows = c.fetchall()
    conn.close()
    return [
        {
            "id": r["id"],
            "code": r["code"],
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(r["timestamp"])),
        }
        for r in rows
    ]


def get_last_timestamp() -> int:
    if _last_scanned_at:
        return _last_scanned_at
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT MAX(timestamp) FROM scans")
    row = c.fetchone()
    conn.close()
    return row[0] or 0
