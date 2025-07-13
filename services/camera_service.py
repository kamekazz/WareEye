import sqlite3
from typing import Dict, List, Optional

DB_PATH = "cameras.db"


def init_db() -> None:
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        """CREATE TABLE IF NOT EXISTS cameras (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            zone TEXT,
            ip_address TEXT,
            url TEXT,
            password TEXT
        )"""
    )
    conn.commit()
    conn.close()


def _row_to_dict(row: sqlite3.Row) -> Dict:
    return {
        "id": row["id"],
        "name": row["name"],
        "zone": row["zone"],
        "ip_address": row["ip_address"],
        "url": row["url"],
        "password": row["password"],
    }


def get_all() -> List[Dict]:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM cameras")
    rows = c.fetchall()
    conn.close()
    return [_row_to_dict(r) for r in rows]


def get(camera_id: int) -> Optional[Dict]:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM cameras WHERE id=?", (camera_id,))
    row = c.fetchone()
    conn.close()
    return _row_to_dict(row) if row else None


def create(name: str, zone: str, ip_address: str, url: str, password: str) -> None:
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        "INSERT INTO cameras (name, zone, ip_address, url, password) VALUES (?, ?, ?, ?, ?)",
        (name, zone, ip_address, url, password),
    )
    conn.commit()
    conn.close()


def update(camera_id: int, name: str, zone: str, ip_address: str, url: str, password: str) -> None:
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        """UPDATE cameras
           SET name=?, zone=?, ip_address=?, url=?, password=?
           WHERE id=?""",
        (name, zone, ip_address, url, password, camera_id),
    )
    conn.commit()
    conn.close()


def delete(camera_id: int) -> None:
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("DELETE FROM cameras WHERE id=?", (camera_id,))
    conn.commit()
    conn.close()
