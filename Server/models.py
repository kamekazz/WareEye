from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Scan(db.Model):
    """Database model for a scan event."""

    id = db.Column(db.Integer, primary_key=True)
    camera_name = db.Column(db.String, nullable=False, index=True)
    area = db.Column(db.String, nullable=False, index=True)
    camera_type = db.Column(db.String, nullable=False)
    client_ip = db.Column(db.String, nullable=False)
    camera_url = db.Column(db.String, nullable=False)
    barcode = db.Column(db.String, nullable=False, index=True)
    timestamp = db.Column(db.DateTime, nullable=False, index=True, default=datetime.utcnow)

    def __repr__(self) -> str:  # pragma: no cover - representation only
        return f"<Scan {self.id} {self.barcode}>"
