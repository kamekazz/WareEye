from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Scan(db.Model):
    """Database model for a scan event."""

    id = db.Column(db.Integer, primary_key=True)
    camera_name = db.Column(db.String, nullable=False)
    area = db.Column(db.String, nullable=False)
    camera_type = db.Column(db.String, nullable=False)
    client_ip = db.Column(db.String, nullable=False)
    camera_url = db.Column(db.String, nullable=False)
    barcode = db.Column(db.String, nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self) -> str:  # pragma: no cover - representation only
        return f"<Scan {self.id} {self.barcode}>"
