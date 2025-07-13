import sqlite3
from typing import Dict, List, Optional

from ..models.camera import build_url

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
            password TEXT,
            scanning INTEGER DEFAULT 0
        )"""
    )
    # Add scanning column if the table already existed without it
    c.execute("PRAGMA table_info(cameras)")
    cols = [r[1] for r in c.fetchall()]
    if "scanning" not in cols:
        c.execute("ALTER TABLE cameras ADD COLUMN scanning INTEGER DEFAULT 0")
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
        "scanning": bool(row["scanning"]),
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


def create(name: str, zone: str, ip_address: str, password: str, scanning: bool = False) -> None:
    """Create a new camera and generate its stream URL."""
    url = build_url(ip_address, password)
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        "INSERT INTO cameras (name, zone, ip_address, url, password, scanning) VALUES (?, ?, ?, ?, ?, ?)",
        (name, zone, ip_address, url, password, int(scanning)),
    )
    conn.commit()
    conn.close()


def update(camera_id: int, name: str, zone: str, ip_address: str, password: str, scanning: bool = False) -> None:
    """Update an existing camera, regenerating its URL."""
    url = build_url(ip_address, password)
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        """UPDATE cameras
           SET name=?, zone=?, ip_address=?, url=?, password=?, scanning=?
           WHERE id=?""",
        (name, zone, ip_address, url, password, int(scanning), camera_id),
    )
    conn.commit()
    conn.close()


def delete(camera_id: int) -> None:
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("DELETE FROM cameras WHERE id=?", (camera_id,))
    conn.commit()
    conn.close()


def toggle_scanning(camera_id: int) -> Optional[bool]:
    """Toggle the scanning flag for a camera and return the new state.

    Returns ``None`` if the camera does not exist."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT scanning FROM cameras WHERE id=?", (camera_id,))
    row = c.fetchone()
    if row is None:
        conn.close()
        return None

    new_value = 0 if row[0] else 1
    c.execute("UPDATE cameras SET scanning=? WHERE id=?", (new_value, camera_id))
    conn.commit()
    conn.close()
    return bool(new_value)
